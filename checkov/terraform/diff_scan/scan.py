"""Full, baseline and diff-files-only scans. All three run Checkov's runner on the resulting graph the same way.

  full      parse the tree + build_pre_render_graph() + render                         (the oracle)
  baseline  the same build, plus the v2 artifact (pre-render capture + resource-level rendered export)
  diff      NO repository parse: DiffEngine builds the pre-render graph from the artifact + changed files,
            incremental_graph.update_graph() re-renders only affected vertices, the runner reads repository files
            from the in-memory index (CHECKOV_DIFF_FILES_ONLY)
"""
from __future__ import annotations

import contextlib
import dataclasses
import os

from dataclasses import dataclass
from typing import Any, Iterator, Optional

from checkov.common.graph.graph_builder.deterministic import REALPATH_MEMO_ENV, STABLE_KEY_CACHE_ENV
from checkov.common.graph.graph_builder.variable_rendering.affected_schedule import AFFECTED_SCHEDULE_ENV, \
    SUBGRAPH_SCHEDULE_ENV
from checkov.common.output.report import Report
from checkov.terraform.graph_builder.foreach.subgraph_scope import SCOPE_ENV as SUBGRAPH_SCOPE_ENV
from checkov.terraform.graph_builder.variable_rendering.safe_eval_functions import REUSE_ASTEVAL_ENV
from checkov.common.graph.graph_builder.graph_components.blocks import REUSE_JSONPATH_PARSER_ENV
from checkov.common.util.env_vars_config import env_vars_config
from checkov.runner_filter import RunnerFilter
from checkov.terraform.diff_files_only import DIFF_FILES_ONLY_ENV, repository_files
from checkov.terraform.graph_builder import incremental_graph
from checkov.terraform.graph_builder.local_graph import TerraformLocalGraph
from checkov.terraform.graph_builder.variable_rendering.renderer import TerraformVariableRenderer
from checkov.terraform.runner import Runner

from checkov.common.util.data_structures_utils import pickle_deepcopy
from checkov.terraform.graph_builder.graph_components.block_types import BlockType

from checkov.terraform.diff_scan import inputs, tfvars
from checkov.terraform.diff_scan.tfvars import is_terraform_file
from checkov.terraform.diff_scan.artifact import dumps
from checkov.terraform.diff_scan.artifact_store import RECORD_ENCODING, decode_record, encode_record
from checkov.terraform.diff_scan.baseline import capture_pre_render, creation_digest
from checkov.terraform.diff_scan.expansions import MODULE_LEVEL_REUSE_ENV, PRECISE_CLOSURE_ENV, ExpansionRecorder
from checkov.terraform.diff_scan.instance_update import INSTANCE_UPDATE_ENV
from checkov.terraform.diff_scan.engine import NEGATIVE_CONTROL, ChangeSet, DiffEngine, PreRenderReport, \
    RESOURCE_LEVEL_UNITS_ENV, REUSE_EXPANSIONS_ENV
from checkov.terraform.diff_scan.relocate import relocate_artifact
from checkov.terraform.graph_builder.utils import NESTED_PREFIX_INDEX_ENV
from checkov.terraform.diff_scan.rename import RENAME_REMAP_ENV, apply_renames, pairs_report
from checkov.terraform.diff_scan.module_files import MODULE_FILE_SET_ENV
from checkov.terraform.graph_builder.foreach.module_handler import SKIP_EMPTY_LEVEL_RENDER_ENV
from checkov.terraform.diff_scan.graph_ops import edge_tuples, permute, set_edges
from checkov.terraform.diff_scan.recorder import EdgeRecorder
from checkov.terraform.diff_scan.scanner_inputs import MATERIALIZED_DIR, external_modules, is_external_module_path, \
    var_files_from_env


FLAGS = {
    "CHECKOV_DETERMINISTIC_GRAPH": "true",
    "CHECKOV_INCREMENTAL_GRAPH": "true",
    "CHECKOV_ISOLATE_CHECK_CONFIG": "true",
}
"""Every scan mode (full oracle, baseline, diff) runs with the same opt-in flags."""


def enable_flags() -> None:
    for name, value in FLAGS.items():
        os.environ[name] = value


def _definitions_context(runner: Runner) -> dict[Any, Any]:
    from checkov.terraform.context_parsers.registry import parser_registry

    context: dict[Any, Any] = {}
    for definition in (runner.definitions or {}).items():
        context = parser_registry.enrich_definitions_context(definitions=definition, collect_skip_comments=True)
    return context


@contextlib.contextmanager
def _module_cache(modules_cache: dict[str, Any]) -> Iterator[None]:
    from checkov.terraform.module_loading.registry import module_loader_registry

    previous = module_loader_registry.module_content_cache
    module_loader_registry.module_content_cache = dict(modules_cache)
    try:
        yield
    finally:
        module_loader_registry.module_content_cache = previous


@dataclass
class ScanResult:
    graph: Any
    report: Report
    artifact: Optional[dict[str, Any]] = None
    pre_render: Optional[PreRenderReport] = None
    render: Optional[incremental_graph.UpdateReport] = None
    validation: Optional[inputs.ValidationReport] = None


SMALL_SECTIONS = ("version", "root", "foreach_ran", "order_matches_definitions", "units_isolated", "cross_unit_links",
                  "tf_var_environment", "tfvar_vertices", "aliases", "alias_keys", "module", "tfvar_blocks")
"""Sections kept in memory until the end of the baseline (`artifact` stays a dict of them, for the CLI's summary);
every other section of a section-store baseline is written to disk as soon as it is produced."""


class _BaselineBuilder:
    def __init__(self, root: str, writer: Optional[Any] = None) -> None:
        self.root = root
        self.artifact: Optional[dict[str, Any]] = None
        self.writer = writer
        """section-store baseline (artifact_store.SectionWriter): big sections go to disk when produced, rendered
        vertex records are msgpack-encoded as they are exported"""

    def build(self, graph: TerraformLocalGraph) -> None:
        tfvar_blocks = [b for b in graph.module.blocks if b.block_type == BlockType.TF_VARIABLE]
        tfvar_blocks = pickle_deepcopy(tfvar_blocks)
        recorder = EdgeRecorder(graph, self.root)
        recorder.install()
        expansion_recorder = ExpansionRecorder(self.root)
        graph.foreach_statement_oracle = expansion_recorder
        try:
            graph.build_pre_render_graph()
        finally:
            recorder.uninstall()
            del graph.foreach_statement_oracle
        digests = [creation_digest(block, self.root) for block in graph.vertices]
        pre_render = capture_pre_render(graph, recorder, digests, self.root,
                                        sink=self._write_big_section if self.writer is not None else None)
        recorder.probes.clear()
        recorder.edge_owners.clear()
        pre_render["tfvar_blocks"] = [dumps(b) for b in tfvar_blocks]
        pre_render["expansions"] = expansion_recorder.records
        self.artifact = self.spill(pre_render)
        rendered = _render_and_export(graph, self.root, encode_vertices=self.writer is not None, writer=self.writer)
        if self.writer is not None:
            for name in ("vertices", "edges"):
                self.writer.write(f"rendered.{name}", rendered.pop(name))
        self.artifact["rendered"] = rendered

    def _write_big_section(self, name: str, value: Any) -> bool:
        """capture_pre_render sink: write a big section now (True), keep a small one in memory (False)."""
        if name in SMALL_SECTIONS:
            return False
        self.writer.write(name, value)
        return True

    def spill(self, sections: dict[str, Any]) -> dict[str, Any]:
        """Write every big section now and keep only the small ones (section-store baselines)."""
        if self.writer is None:
            return sections
        for name in [n for n in sections if n not in SMALL_SECTIONS]:
            self.writer.write(name, sections.pop(name))
        return sections


RENDERED_SUBSECTIONS = ("vertices", "edges", "pre_render")
"""The v3 store keeps the big parts of the rendered export as their own sections ("rendered.vertices", ...), so each
is decoded only when update_graph reads it and released right after."""


class RenderedView:
    """update_graph's view of the rendered export of a v3 store: the small `rendered` section plus the split-out big
    parts, decoded on first access."""

    def __init__(self, artifact: Any) -> None:
        self._artifact = artifact
        self._small = artifact["rendered"]
        self._decoder = decode_record if self._small.get("vertices_encoding") == RECORD_ENCODING else None

    def __getitem__(self, name: str) -> Any:
        if name in RENDERED_SUBSECTIONS:
            return self._artifact[f"rendered.{name}"]
        if name == "vertex_decoder":
            return self._decoder
        return self._small[name]

    def get(self, name: str, default: Any = None) -> Any:
        if name in RENDERED_SUBSECTIONS:
            return self._artifact.get(f"rendered.{name}", default)
        if name == "vertex_decoder":
            return self._decoder
        return self._small.get(name, default)

    def __contains__(self, name: object) -> bool:
        return name in RENDERED_SUBSECTIONS or name in self._small

    def release_part(self, name: str) -> None:
        _release(self._artifact, f"rendered.{name}")

    def release(self) -> None:
        _release(self._artifact, "rendered", *(f"rendered.{name}" for name in RENDERED_SUBSECTIONS))


def _render(artifact: Any, graph: TerraformLocalGraph, root: str) -> incremental_graph.UpdateReport:
    """update_graph on the rendered export; its serialized form is released before the edge loop starts."""
    if "rendered.vertices" in artifact:
        view = RenderedView(artifact)
        return incremental_graph.update_graph(view, graph, root, release=view.release)
    return incremental_graph.update_graph(artifact["rendered"], graph, root,
                                          release=lambda: _release(artifact, "rendered"))


def _render_and_export(graph: TerraformLocalGraph, root: str, encode_vertices: bool,
                       writer: Optional[Any] = None) -> dict[str, Any]:
    """Render the baseline graph and export it. With a section `writer`, the resource-level pre-render capture is
    written to disk before rendering starts (it is not needed again by the baseline) instead of being held through
    the render."""
    resource_level_pre_render = incremental_graph.capture_pre_render(graph, root)
    pre_clock = incremental_graph.anonymise(resource_level_pre_render.get("clock_keys", []), root)
    if writer is not None:
        writer.write("rendered.pre_render", incremental_graph.anonymise(resource_level_pre_render, root))
        resource_level_pre_render = {"clock_keys": pre_clock}
    renderer = TerraformVariableRenderer(graph)
    unconverged: set[str] = set()
    loop_end: dict[str, Any] = {}

    def capture() -> None:
        unconverged.update(incremental_graph.unconverged_vertices(renderer, graph, root))
        loop_end.update(incremental_graph.capture_loop_end(graph, root))

    renderer.on_edge_loop_end = capture
    renderer.render_variables_from_local_graph()
    graph.update_vertices_fields()
    graph.build_post_render_edges()
    encode = encode_record if encode_vertices else None
    exported = incremental_graph.export_graph(graph, root, resource_level_pre_render, unconverged, loop_end, encode)
    if writer is not None:
        del exported["pre_render"]
    if encode_vertices:
        exported["vertices_encoding"] = RECORD_ENCODING
    return exported


class _ShuffledBuilder:
    """Experiment: a full build whose pre-render vertex list is randomly permuted before rendering."""

    def __init__(self, seed: int) -> None:
        self.seed = seed
        self.artifact = None

    def build(self, graph: TerraformLocalGraph) -> None:
        import random

        graph.build_pre_render_graph()
        rng = random.Random(self.seed)
        order = list(range(len(graph.vertices)))
        rng.shuffle(order)
        permute(graph, order)
        edges = edge_tuples(graph)
        rng.shuffle(edges)
        set_edges(graph, edges)
        graph.render_and_finalize_graph()


@contextlib.contextmanager
def _graph_builder(builder: Any) -> Iterator[None]:
    if builder is None:
        yield
        return
    original = TerraformLocalGraph.build_graph
    TerraformLocalGraph.build_graph = lambda graph, render_variables=True: builder.build(graph)
    try:
        yield
    finally:
        TerraformLocalGraph.build_graph = original


def _run_checks(runner: Runner, graph: TerraformLocalGraph, root: str) -> Report:
    resources_report = Report(runner.check_type)
    runner._update_definitions_and_breadcrumbs([(None, graph)], resources_report, root)
    runner.context = _definitions_context(runner)
    report = runner.run(root_folder=root, runner_filter=RunnerFilter(framework=["terraform"], show_progress_bar=False,
                                                                     download_external_modules=False))
    report = report[0] if isinstance(report, list) else report
    report.resources |= resources_report.resources
    return report


def _parsed_scan(root: str, builder: Any) -> ScanResult:
    runner = Runner()
    modules = external_modules(root)
    supplied = sorted(modules)
    """the pre-scan's module inputs (Checkov's loader later adds derived keys for nested / //subdir modules)"""
    recording = isinstance(builder, _BaselineBuilder)
    if recording:
        calls, variable_files, uninstall = tfvars.record_calls(runner.graph_manager.parser)
    with _module_cache(modules), _graph_builder(builder):
        graph, _ = runner.graph_manager.build_graph_from_source_directory(
            source_dir=root, local_graph_class=TerraformLocalGraph, download_external_modules=False,
            external_modules_content_cache=modules, vars_files=var_files_from_env(root))
    if recording:
        uninstall()
        builder.artifact.update(builder.spill({"variable_inputs": {
            "calls": [dataclasses.asdict(c) for c in calls],
            "files": variable_files,
            "var_files": var_files_from_env(root) or [],
            "external_vars": dumps(runner.graph_manager.parser.external_vars),
            "external_modules": supplied,
        }}))
        from checkov.terraform.diff_scan.scoped_checks import run_and_capture_baseline_checks
        from checkov.terraform.graph_builder.incremental_graph import vertex_keys
        report, f_meta, f_verts = run_and_capture_baseline_checks(
            runner, graph, root, vertex_keys(graph, root), encode=builder.writer is not None
        )
        if builder.writer is not None:
            builder.writer.write("findings.meta", f_meta)
            builder.writer.write("findings.vertices", f_verts)
        else:
            builder.artifact["findings.meta"] = f_meta
            builder.artifact["findings.vertices"] = f_verts
        return ScanResult(graph=graph, report=report, artifact=builder.artifact)
    return ScanResult(graph=graph, report=_run_checks(runner, graph, root),
                      artifact=builder.artifact if builder else None)


def _prepare(root: str) -> str:
    enable_flags()
    env_vars_config.RAW_TF_IN_GRAPH_ENV = True
    return os.path.realpath(root)


def full_scan(root: str) -> ScanResult:
    return _parsed_scan(_prepare(root), None)


def shuffled_full_scan(root: str, seed: int) -> ScanResult:
    return _parsed_scan(_prepare(root), _ShuffledBuilder(seed))


def baseline_scan(root: str, commit: Optional[str] = None, fingerprint: Optional[str] = None,
                  writer: Optional[Any] = None) -> ScanResult:
    """`commit`: the commit `root` is a checkout of. With it, the artifact records the commit, every file's blob SHA
    and the configuration fingerprint, and every PR scan against it must prove its diff starts there (inputs.py).
    `writer`: an artifact_store.SectionWriter: the artifact is written as a v3 section store while the scan runs
    (big sections leave memory as soon as they are produced); the caller commits it."""
    root = _prepare(root)
    baseline_defaults()
    if writer is not None:
        writer.root = root
    result = _parsed_scan(root, _BaselineBuilder(root, writer))
    if commit and result.artifact is not None:
        result.artifact["baseline_inputs"] = inputs.BaselineInputs(
            commit=commit, manifest=inputs.tree_manifest(root), config_fingerprint=fingerprint or "").to_json()
    return result


def _repository_relative(path: str, root: str) -> str:
    return os.path.relpath(path, root).replace(os.sep, "/")


def validate_scan_inputs(artifact: dict[str, Any], changes: ChangeSet, root: str,
                         target: Optional[inputs.ScanTarget], fingerprint: Optional[str]) \
        -> Optional[inputs.ValidationReport]:
    """The diff must be exactly the baseline -> scan-target-tree diff (inputs.validate). Artifacts without commit data
    (PoC harness baselines) are accepted unvalidated only when no scan target is given either."""
    baseline = inputs.BaselineInputs.from_json(artifact.get("baseline_inputs"))
    if baseline is None and target is None:
        return None
    if NEGATIVE_CONTROL == "no_input_validation":
        return None
    changed: dict[str, bytes] = {}
    for path in changes.changed:
        with open(path, "rb") as f:
            changed[_repository_relative(path, root)] = f.read()
    deleted = [_repository_relative(p, root) for p in changes.deleted]
    return inputs.validate(baseline, target, changed, deleted, fingerprint or "")


def repository_index(artifact: dict[str, Any], changes: ChangeSet, root: str,
                     release_files: bool = False) -> Any:
    """Files the runner reads after the graph is built: stored contents of unchanged repository files, the PR's
    changed .tf files, and the external modules the pre-scan materialised for THIS scan (they may differ from the
    baseline's: version bump, upstream change)."""
    gone = set(changes.deleted) | set(changes.changed)
    stored = artifact["files"]
    if release_files:
        _release(artifact, "files")
    if isinstance(stored, dict) and not any(is_external_module_path(p, root) for p in stored) \
            and not os.path.isdir(os.path.join(root, MATERIALIZED_DIR)):
        for p in gone:
            stored.pop(p, None)
        for path in changes.changed:
            if is_terraform_file(path):
                with open(path, "r") as f:
                    stored[path] = f.readlines()
        return stored
    files = {path: lines for path, lines in stored.items()
             if path not in gone and not is_external_module_path(path, root)}
    del stored
    for path in changes.changed:
        if is_terraform_file(path):
            with open(path, "r") as f:
                files[path] = f.readlines()
    for directory, _, names in os.walk(os.path.join(root, MATERIALIZED_DIR)):
        for name in names:
            if name.endswith(".tf"):
                with open(os.path.join(directory, name)) as f:
                    files[os.path.join(directory, name)] = f.readlines()
    return files


PRE_RENDER_ONLY_SECTIONS = ("vertices", "creation_digests", "fingerprints", "edges", "probes", "aliases", "alias_keys",
                            "source_module", "module_connections", "tfvar_vertices", "tfvar_blocks", "unit_by_vertex",
                            "units", "keys", "expansions", "definitions")
"""Artifact sections only the pre-render build reads: released once the PR's pre-render graph exists. `definitions`
stays (post-render passes read baseline definitions lazily through module.temp_tf_definition), `files` is copied into
the repository index and released, `rendered` is released by update_graph's caller once rendering is done."""


def _release(artifact: Any, *names: str) -> None:
    release = getattr(artifact, "release", None)
    if release is not None:
        release(*names)


def _apply_renames(artifact: Any, root: str, changes: ChangeSet) -> list[tuple[str, str]]:
    """Order-preserving pure renames are applied to the artifact (rename.py); `changes` loses those pairs. Runs after
    input validation, which checks the original change set against the scan target."""
    encoded = "rendered.vertices" in artifact and artifact["rendered"].get("vertices_encoding") == RECORD_ENCODING
    changed, deleted, pairs = apply_renames(artifact, root, changes.changed, changes.deleted, encoded)
    changes.changed[:] = changed
    changes.deleted[:] = deleted
    return pairs


def baseline_defaults() -> None:
    """Writer-side defaults of the diff-scan baseline (a reader handles both layouts)."""
    os.environ.setdefault("CHECKOV_DIFF_INDEXED_RECORDS", "true")


def diff_scan(root: str, artifact: Any, changes: ChangeSet, target: Optional[inputs.ScanTarget] = None,
              fingerprint: Optional[str] = None) -> ScanResult:
    """`artifact`: the decoded v2 dict, or an ArtifactSections view of a v3 section store (sections are decoded on
    first use and released after their last use)."""
    root = _prepare(root)
    validation = validate_scan_inputs(artifact, changes, root, target, fingerprint)
    os.environ[DIFF_FILES_ONLY_ENV] = "true"
    os.environ.setdefault(AFFECTED_SCHEDULE_ENV, "true")
    os.environ.setdefault(REALPATH_MEMO_ENV, "true")
    os.environ.setdefault(STABLE_KEY_CACHE_ENV, "true")
    os.environ.setdefault(SUBGRAPH_SCOPE_ENV, "true")
    os.environ.setdefault(incremental_graph.UNCONVERGED_RULE_ENV, "true")
    os.environ.setdefault(SUBGRAPH_SCHEDULE_ENV, "true")
    os.environ.setdefault(REUSE_ASTEVAL_ENV, "true")
    os.environ.setdefault(REUSE_JSONPATH_PARSER_ENV, "true")
    os.environ.setdefault(RESOURCE_LEVEL_UNITS_ENV, "true")
    os.environ.setdefault(REUSE_EXPANSIONS_ENV, "true")
    os.environ.setdefault(INSTANCE_UPDATE_ENV, "true")
    os.environ.setdefault(PRECISE_CLOSURE_ENV, "true")
    os.environ.setdefault(RENAME_REMAP_ENV, "true")
    os.environ.setdefault(MODULE_FILE_SET_ENV, "true")
    os.environ.setdefault(MODULE_LEVEL_REUSE_ENV, "true")
    os.environ.setdefault(SKIP_EMPTY_LEVEL_RENDER_ENV, "true")
    os.environ.setdefault(incremental_graph.CLOCK_EVALUATED_RULE_ENV, "true")
    os.environ.setdefault(incremental_graph.REREAD_FINAL_STATES_ENV, "true")
    os.environ.setdefault("CHECKOV_DIFF_SCOPED_CHECKS", "true")
    os.environ.setdefault("CHECKOV_INCREMENTAL_LAZY_FINAL_STATE", "true")
    os.environ.setdefault(NESTED_PREFIX_INDEX_ENV, "true")
    if NEGATIVE_CONTROL != "no_relocation":
        artifact = relocate_artifact(artifact, root)
    renames = _apply_renames(artifact, root, changes)
    modules = external_modules(root)
    engine = DiffEngine(artifact, root, changes)
    engine.report.renamed_files = pairs_report(renames, root)
    engine.supplied_modules = sorted(modules)
    engine.validate_inputs()
    with _module_cache(modules):
        graph = engine.build()
    engine.report.module_file_set["frozen_callers"] = engine.install_resolved_swaps(graph)
    engine.release_pre_render_state()
    _release(artifact, *PRE_RENDER_ONLY_SECTIONS)
    render = _render(artifact, graph, root)
    pre_render = engine.finish()
    from checkov.terraform.diff_scan.scoped_checks import run_scoped_diff_checks
    runner = Runner()
    changed_files_set = set(engine.changes.changed) | set(engine.changes.deleted)
    if os.getenv("DFO_NEGATIVE", "") == "scope_radius_minus_one":
        effective_affected = set(render.affected_indices)
    else:
        effective_affected = set(render.affected_indices) | set(render.post_render_changed_indices)
    scoped_report = run_scoped_diff_checks(
        runner, graph, root, artifact, effective_affected, changed_files_set
    )
    if scoped_report is None:
        repository_files.set_files(repository_index(artifact, engine.changes, root, release_files=True))
        report = _run_checks(runner, graph, root)
    else:
        report = scoped_report
    _release(artifact, "files", "findings.meta", "findings.vertices", "rendered", "rendered.edges",
             "rendered.pre_render")
    if not os.getenv("CHECKOV_DIFF_SNAPSHOT_OUT"):
        _release(artifact, "rendered.vertices")
    return ScanResult(graph=graph, report=report, pre_render=pre_render, render=render, validation=validation)
