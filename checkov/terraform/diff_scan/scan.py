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

from checkov.terraform.diff_scan import tfvars
from checkov.terraform.diff_scan.tfvars import is_terraform_file
from checkov.terraform.diff_scan.artifact import dumps
from checkov.terraform.diff_scan.baseline import capture_pre_render, creation_digest
from checkov.terraform.diff_scan.engine import NEGATIVE_CONTROL, ChangeSet, DiffEngine, PreRenderReport, \
    RESOURCE_LEVEL_UNITS_ENV
from checkov.terraform.diff_scan.relocate import relocate_artifact
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


class _BaselineBuilder:
    def __init__(self, root: str) -> None:
        self.root = root
        self.artifact: Optional[dict[str, Any]] = None

    def build(self, graph: TerraformLocalGraph) -> None:
        tfvar_blocks = [b for b in graph.module.blocks if b.block_type == BlockType.TF_VARIABLE]
        tfvar_blocks = pickle_deepcopy(tfvar_blocks)
        recorder = EdgeRecorder(graph, self.root)
        recorder.install()
        try:
            graph.build_pre_render_graph()
        finally:
            recorder.uninstall()
        digests = [creation_digest(block, self.root) for block in graph.vertices]
        pre_render = capture_pre_render(graph, recorder, digests, self.root)
        pre_render["tfvar_blocks"] = [dumps(b) for b in tfvar_blocks]
        self.artifact = {**pre_render, "rendered": _render_and_export(graph, self.root)}


def _render_and_export(graph: TerraformLocalGraph, root: str) -> dict[str, Any]:
    resource_level_pre_render = incremental_graph.capture_pre_render(graph, root)
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
    return incremental_graph.export_graph(graph, root, resource_level_pre_render, unconverged, loop_end)


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
        builder.artifact["variable_inputs"] = {
            "calls": [dataclasses.asdict(c) for c in calls],
            "files": variable_files,
            "var_files": var_files_from_env(root) or [],
            "external_vars": dumps(runner.graph_manager.parser.external_vars),
            "external_modules": supplied,
        }
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


def baseline_scan(root: str) -> ScanResult:
    root = _prepare(root)
    return _parsed_scan(root, _BaselineBuilder(root))


def repository_index(artifact: dict[str, Any], changes: ChangeSet, root: str) -> dict[str, list[str]]:
    """Files the runner reads after the graph is built: stored contents of unchanged repository files, the PR's
    changed .tf files, and the external modules the pre-scan materialised for THIS scan (they may differ from the
    baseline's: version bump, upstream change)."""
    gone = set(changes.deleted) | set(changes.changed)
    files = {path: lines for path, lines in artifact["files"].items()
             if path not in gone and not is_external_module_path(path, root)}
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


def diff_scan(root: str, artifact: dict[str, Any], changes: ChangeSet) -> ScanResult:
    root = _prepare(root)
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
    if NEGATIVE_CONTROL != "no_relocation":
        artifact = relocate_artifact(artifact, root)
    modules = external_modules(root)
    engine = DiffEngine(artifact, root, changes)
    engine.supplied_modules = sorted(modules)
    engine.validate_inputs()
    repository_files.set_files(repository_index(artifact, engine.changes, root))
    with _module_cache(modules):
        graph = engine.build()
    render = incremental_graph.update_graph(artifact["rendered"], graph, root)
    pre_render = engine.finish()
    report = _run_checks(Runner(), graph, root)
    return ScanResult(graph=graph, report=report, pre_render=pre_render, render=render)
