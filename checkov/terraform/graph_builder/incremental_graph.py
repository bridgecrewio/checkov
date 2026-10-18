"""Resource-level incremental Terraform graph (opt-in: CHECKOV_DETERMINISTIC_GRAPH=true + CHECKOV_INCREMENTAL_GRAPH=true).

Nothing in this module runs unless a caller invokes it explicitly; the regular build_graph() path is unchanged.

Baseline:  export_graph(graph, root)            -> JSON-safe artifact of the RENDERED graph (stable vertex keys)
PR scan:   update_graph(artifact, root, ...)    -> a TerraformLocalGraph equal to a full build of the PR tree, where
           only the affected vertices are re-rendered and every other vertex is loaded from the artifact

How the PR graph is produced
  1. pre  = the PR tree's pre-render graph (parse + vertices + edges + count/for_each expansion; no rendering)
  2. affected = blocks whose pre-render state differs from the baseline's, closed over:
       * referrers: every vertex that transitively references an affected vertex (pre-render edges)
       * expansion: every instance of a counted / for_each block (and its main vertex) when any is affected
       * providers: every resource of the same directory when a provider block changed
       * vertices that are new, or whose baseline render did not converge
     anything else is `frozen`: its exported rendered state is copied onto the pre-render vertex
  3. the renderer runs on the full PR graph with frozen_vertices set: frozen vertices are never written, the edge loop
     keeps its global schedule, the post-loop passes skip frozen vertices
  4. post-render passes (breadcrumbs, module addresses, provider attributes) and post-render edges run on the whole
     graph: they derive state from already-final vertex data and are idempotent on frozen vertices

Rendered state is restored with the vertices' pre-render identity, so vertex indices in breadcrumbs are remapped from
stable keys to the PR graph's indices.
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
from dataclasses import dataclass, field
from typing import Any, Optional

from checkov.common.graph.graph_builder.deterministic import incremental_graph_enabled, module_chain_key
from checkov.common.graph.graph_builder.variable_rendering.breadcrumb_metadata import BreadcrumbMetadata
from checkov.common.util.json_utils import CustomJSONEncoder
from checkov.terraform.graph_builder.graph_components.block_types import BlockType
from checkov.terraform.graph_builder.graph_components.blocks import TerraformBlock
from checkov.terraform.modules.module_objects import TFModule

ARTIFACT_VERSION = 1
ROOT = "<root>"


class IncrementalGraphUnsupported(Exception):
    """The change cannot be applied incrementally with a correctness guarantee: the caller must rebuild."""


@dataclass
class UpdateReport:
    vertices: int = 0
    affected: int = 0
    frozen: int = 0
    changed_blocks: list[str] = field(default_factory=list)
    removed_blocks: list[str] = field(default_factory=list)
    reasons: dict[str, int] = field(default_factory=dict)
    render_waves: int = 0
    edges_evaluated: int = 0
    """edge evaluations actually performed by the renderer (frozen-origin edges are skipped)"""
    vertices_written: int = 0
    """distinct vertices the renderer wrote an attribute to (must be a subset of the affected set)"""
    frozen_written: int = 0
    """frozen vertices the renderer wrote to: must be 0 (verifies that unchanged vertices are not re-rendered)"""
    edge_loop_rounds: list[int] = field(default_factory=list)
    """[baseline, PR] rounds of the global edge loop (precise unconverged rule)"""
    edge_schedule: dict[str, Any] = field(default_factory=dict)
    """whether the affected-only edge schedule replaced the global edge loop (renderer.schedule_stats)"""


def _require_flag() -> None:
    if not incremental_graph_enabled():
        raise RuntimeError("incremental graph requires CHECKOV_DETERMINISTIC_GRAPH=true and CHECKOV_INCREMENTAL_GRAPH=true")


TUPLE_MARKER = "__dfo_tuple__"
"""Checkov's renderer leaves some evaluated values as Python TUPLES (e.g. a `"${join(",", ...)}"` string the evaluator
split into a tuple). Checkov's final passes treat tuples and lists differently (get_origin_attributes flattens only
lists into `key.0` / `key.1` attributes), so a frozen vertex restored with a list where the full scan holds a tuple
gains attributes the full scan does not have. JSON has no tuples: they are wrapped as {TUPLE_MARKER: [...]} in the
export and unwrapped on restore."""


def _mark_tuples(value: Any) -> Any:
    if isinstance(value, tuple):
        return {TUPLE_MARKER: [_mark_tuples(v) for v in value]}
    if isinstance(value, list):
        return [_mark_tuples(v) for v in value]
    if isinstance(value, dict):
        return {k: _mark_tuples(v) for k, v in value.items()}
    return value


def _unmark_tuples(value: Any) -> Any:
    if isinstance(value, dict):
        if len(value) == 1 and TUPLE_MARKER in value:
            return tuple(_unmark_tuples(v) for v in value[TUPLE_MARKER])
        return {k: _unmark_tuples(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_unmark_tuples(v) for v in value]
    return value


def _preserve_tuples() -> bool:
    return os.getenv("DFO_NEGATIVE", "") != "export_drops_tuples"


def _anonymise(value: Any, root: str) -> Any:
    """Insertion order is kept: consumers read vertex configs positionally (e.g. the module context parser takes the
    first key of a module call's config as its name; a counted call also holds `virtual_resources`)."""
    text = json.dumps(value, cls=CustomJSONEncoder, sort_keys=False, default=str)
    return json.loads(text.replace(root, ROOT))


def _anonymise_state(value: Any, root: str) -> Any:
    """Rendered vertex state (attributes / config) for the export: tuples preserved (TUPLE_MARKER)."""
    return _anonymise(_mark_tuples(value) if _preserve_tuples() else value, root)


def anonymise(value: Any, root: str) -> Any:
    """Public form of _anonymise (root replaced by the placeholder, JSON-safe)."""
    return _anonymise(value, root)


def _anonymised_text(value: Any, root: str) -> str:
    value = _mark_tuples(value) if _preserve_tuples() else value
    return json.dumps(value, cls=CustomJSONEncoder, sort_keys=False, default=str).replace(root, ROOT)


def _restore(value: Any, root: str) -> Any:
    restored = json.loads(json.dumps(value).replace(ROOT, root))
    return _unmark_tuples(restored) if _preserve_tuples() else _tuples_as_lists(_unmark_tuples(restored))


def _tuples_as_lists(value: Any) -> Any:
    """Negative control `export_drops_tuples`: the restore side behaves like the pre-fix export (tuples became
    lists). Applied on the PR side because the harness's baseline worker never sees DFO_NEGATIVE."""
    if isinstance(value, tuple):
        return [_tuples_as_lists(v) for v in value]
    if isinstance(value, list):
        return [_tuples_as_lists(v) for v in value]
    if isinstance(value, dict):
        return {k: _tuples_as_lists(v) for k, v in value.items()}
    return value


def vertex_key(vertex: TerraformBlock, root: str) -> str:
    identity = [vertex.path, [list(m) for m in module_chain_key(vertex.source_module_object)], vertex.block_type,
                vertex.name, vertex.for_each_index]
    if vertex.block_type == BlockType.TF_VARIABLE:
        identity.append(vertex.attributes.get("load_dir"))
    return json.dumps(_anonymise(identity, root), sort_keys=True)


def block_key(key: str) -> str:
    """Key of the source block an (expanded) vertex comes from: instance indices removed."""
    identity = json.loads(key)
    chain = [[path, name, None] for path, name, _ in identity[1]]
    return json.dumps([identity[0], chain, identity[2], identity[3].split("[")[0]], sort_keys=True)


def vertex_keys(graph: Any, root: str) -> list[str]:
    keys = [vertex_key(v, root) for v in graph.vertices]
    seen: dict[str, int] = {}
    for k in keys:
        seen[k] = seen.get(k, 0) + 1
    duplicates = sorted(k for k, n in seen.items() if n > 1)
    if duplicates:
        raise IncrementalGraphUnsupported(f"vertex identity not unique (duplicate block address): {duplicates[:3]}")
    return keys


PATH_RENAMES: list[tuple[str, str]] = []
"""Anonymised file-path renames applied to the baseline artifact (diff_scan.rename): baseline pre-render digests were
computed with the OLD path, so the PR side's digest text maps every NEW path back to its old one before hashing.
Empty outside a diff scan with renames."""


RESOLVED_SWAPS: dict[str, tuple[Any, Any]] = {}
"""Module-call vertex key -> (baseline `__resolved__`, PR `__resolved__`) for callers whose only pre-render change is
the module file list (diff_scan.module_files). Rendering never reads `__resolved__` (only the runner and id helpers
read it from the final config), so such a caller is compared with its baseline value and, when frozen, restored with
the PR's value. Empty outside a diff scan with handled module file-set changes."""


def _swap_resolved(vertex: TerraformBlock, value: Any) -> Any:
    from checkov.common.util.consts import RESOLVED_MODULE_ENTRY_NAME

    call = vertex.config.get(vertex.name) if isinstance(vertex.config, dict) else None
    if not isinstance(call, dict) or RESOLVED_MODULE_ENTRY_NAME not in call:
        return None
    previous = call[RESOLVED_MODULE_ENTRY_NAME]
    call[RESOLVED_MODULE_ENTRY_NAME] = value
    return previous


def pre_render_digest(vertex: TerraformBlock, root: str, keys: Optional[list[str]] = None) -> str:
    """Identity of a vertex's pre-render state: everything rendering starts from.
    `source_module` holds vertex INDICES, which shift whenever any block is added or removed anywhere; with `keys`
    they are replaced by stable keys so an unrelated edit does not invalidate every module vertex."""
    source_module = sorted(keys[i] for i in vertex.source_module) if keys is not None else sorted(vertex.source_module)
    payload = {"attributes": vertex.attributes, "config": vertex.config, "source_module": source_module,
               "foreach_attrs": getattr(vertex, "foreach_attrs", None)}
    text = json.dumps(_anonymise(payload, root), sort_keys=True)
    for old, new in PATH_RENAMES:
        text = text.replace(new, old)
    return hashlib.sha256(text.encode()).hexdigest()


NON_DETERMINISTIC_FUNCTIONS = ("timestamp(",)
"""Functions Checkov evaluates to a different value on every scan (timestamp() renders the wall clock). A vertex
whose source calls one is never frozen; its referrers follow through the closure. Functions Checkov does not
implement (uuid(), plantimestamp(), bcrypt()) stay unrendered text and are deterministic."""


def uses_non_deterministic_function(vertex: TerraformBlock) -> bool:
    text = json.dumps(vertex.attributes, cls=CustomJSONEncoder, default=str)
    return any(f in text for f in NON_DETERMINISTIC_FUNCTIONS)


CLOCK_EVALUATED_RULE_ENV = "CHECKOV_INCREMENTAL_CLOCK_EVALUATED_ONLY"
"""Opt-in (set by the diff scan): a vertex calling timestamp() is re-rendered only if the baseline's render evaluated
the call. Checkov evaluates it only where the surrounding expression is fully resolvable (`b-${timestamp()}`); inside
an expression it cannot evaluate (`x != "" ? x : formatdate("YYYY-MM-DD", timestamp())`) the call stays text in the
final value. Whether the call is evaluated depends only on the vertex's own pre-render state and the values it reads;
any change to those makes the vertex affected through the digest / referrer rules, so an unchanged vertex whose
baseline left every call unevaluated renders to the same text again."""


REREAD_FINAL_STATES_ENV = "CHECKOV_INCREMENTAL_REREAD_FINAL_STATES"
"""Opt-in (set by the diff scan): with an indexed record file (artifact_store.IndexedRecords) the frozen vertices'
final states are read from disk again at the end of the edge loop instead of keeping every record's bytes in memory
through the loop (gcp: ~270 MB of record bytes)."""


def reread_final_states_enabled() -> bool:
    return os.getenv(REREAD_FINAL_STATES_ENV, "false").lower() == "true"


def _is_indexed_records(records: Any) -> bool:
    """Records read from the artifact's record file on access (re-reading costs a seek, not a second copy)."""
    from checkov.terraform.diff_scan.artifact_store import IndexedRecords
    from checkov.terraform.diff_scan.rename import RenamedRecords

    return isinstance(records, (IndexedRecords, RenamedRecords))


def clock_evaluated_only_enabled() -> bool:
    return os.getenv(CLOCK_EVALUATED_RULE_ENV, "false").lower() == "true"


def _baseline_left_clock_unevaluated(record: dict[str, Any]) -> bool:
    """The baseline's final attributes still hold every timestamp() call as text: none was turned into a time."""
    calls_in_source = json.dumps(record["loop_end"]["attributes"]).count(NON_DETERMINISTIC_FUNCTIONS[0])
    calls_in_final = json.dumps(record["attributes"]).count(NON_DETERMINISTIC_FUNCTIONS[0])
    if os.getenv("DFO_NEGATIVE", "") == "clock_rule_ignores_evaluation":
        return True
    return calls_in_final >= calls_in_source > 0


def _needs_clock_rerender(vertex: TerraformBlock, key: str, exported: Any, decode: Any) -> bool:
    if not uses_non_deterministic_function(vertex):
        return False
    if not clock_evaluated_only_enabled():
        return True
    stored = exported[key]
    record = decode(stored) if decode is not None else stored
    return not _baseline_left_clock_unevaluated(record)


# --------------------------------------------------------------------------------------------------- export


def capture_pre_render(graph: Any, root: str) -> dict[str, Any]:
    """Pre-render digests and edges of a graph that has been built up to (not including) rendering."""
    keys = vertex_keys(graph, root)
    return {
        "keys": keys,
        "digests": {k: pre_render_digest(v, root, keys) for k, v in zip(keys, graph.vertices)},
        "edges": sorted({json.dumps([keys[e.origin], keys[e.dest], e.label]) for e in graph.edges}),
    }


def capture_loop_end(graph: Any, root: str) -> dict[str, Any]:
    """Every vertex's attributes and config as they are when the edge loop ends, BEFORE the post-loop passes
    (update_vertices_configs, evaluate_non_rendered_values, dynamic blocks) rewrite them. This is the state referrers
    read during the loop, so it is what a frozen vertex must hold while affected vertices are rendered.
    Held as anonymised JSON text (the exact text _anonymise round-trips), which costs a fraction of the decoded
    structure while the baseline finishes rendering; export_graph decodes each vertex's entry once."""
    keys = vertex_keys(graph, root)
    return {key: _anonymised_text({"attributes": vertex.attributes, "config": vertex.config}, root)
            for key, vertex in zip(keys, graph.vertices)}


def export_graph(graph: Any, root: str, pre_render: dict[str, Any], unconverged: set[str],
                 loop_end: dict[str, Any], encode: Optional[Any] = None) -> dict[str, Any]:
    """The rendered graph as a JSON-safe artifact. `pre_render` from capture_pre_render() on the same build,
    `unconverged`: keys of vertices that still had pending edges when the render loop hit its cap,
    `loop_end`: capture_loop_end() taken at the end of the edge loop of the same build (consumed: emptied here).
    `encode`: optional per-vertex encoder (value -> bytes) applied as each record is built, so the export never holds
    every decoded record at once; consumers decode with the matching decoder."""
    _require_flag()
    root = os.path.realpath(root)
    keys = vertex_keys(graph, root)
    vertices = {}
    for key, vertex in zip(keys, graph.vertices):
        captured = loop_end.pop(key)
        record = _anonymise({
            "loop_end": json.loads(captured) if isinstance(captured, str) else captured,
            "attributes": _mark_tuples(vertex.attributes) if _preserve_tuples() else vertex.attributes,
            "config": _mark_tuples(vertex.config) if _preserve_tuples() else vertex.config,
            "changed_attributes": {attr: [[keys[b.vertex_id], b.attribute_key] for b in crumbs]
                                   for attr, crumbs in vertex.changed_attributes.items()},
            "module_connections": {attr: [keys[i] for i in ids] for attr, ids in vertex.module_connections.items()},
            "foreach_attrs": getattr(vertex, "foreach_attrs", None),
            "dynamic_attributes": getattr(vertex, "dynamic_attributes", None),
            "has_dynamic_block": getattr(vertex, "has_dynamic_block", False),
        }, root)
        vertices[key] = encode(record) if encode is not None else record
    return {
        "version": ARTIFACT_VERSION,
        "vertices": vertices,
        "edges": sorted(json.dumps([keys[e.origin], keys[e.dest], e.label]) for e in graph.edges),
        "pre_render": _anonymise(pre_render, root),
        "unconverged": sorted(unconverged),
        "edge_loop_rounds": _edge_loop_rounds(graph),
    }


# --------------------------------------------------------------------------------------------------- affected set

UNCONVERGED_RULE_ENV = "CHECKOV_INCREMENTAL_PRECISE_UNCONVERGED"
"""Opt-in (set by the diff scan): baseline-unconverged vertices are re-rendered only if the edge loop's length changed."""


def _edge_loop_rounds(graph: Any) -> int:
    from checkov.common.graph.graph_builder.variable_rendering.affected_schedule import edge_loop_rounds
    from checkov.common.graph.graph_builder.variable_rendering.renderer import VariableRenderer

    return edge_loop_rounds(graph, VariableRenderer.MAX_NUMBER_OF_LOOPS)


def _edge_loop_rounds_rule(graph: Any, artifact: dict[str, Any], report: UpdateReport) -> str:
    """'off' (legacy rule: every baseline-unconverged vertex is re-rendered), 'same' or 'changed'.

    A frozen vertex holds the value the baseline's edge loop left in it, which is truncated when that loop stopped at
    its cap. In deterministic mode an edge runs in rounds settle(dest)+1, +3, ... below the loop length, and settle(v)
    depends only on v's downstream edges; a frozen vertex's downstream is unchanged (any change there makes it
    affected through the referrer closure). So with the same loop length a frozen vertex sees exactly the
    evaluations it saw at baseline, converged or not. With a different length, every vertex whose edges can repeat
    is re-rendered. (Settle rounds of all edges form a contiguous range, so the length is 0, 1, 2 or the cap: in
    practice it only changes on graphs whose longest reference chain is 2 or shorter.)"""
    if os.getenv(UNCONVERGED_RULE_ENV, "false").lower() != "true" or "edge_loop_rounds" not in artifact:
        return "off"
    rounds = _edge_loop_rounds(graph)
    report.edge_loop_rounds = [artifact["edge_loop_rounds"], rounds]
    if os.getenv("DFO_NEGATIVE", "") == "unconverged_ignore_loop_length":
        return "same"
    return "same" if rounds == artifact["edge_loop_rounds"] else "changed"


def _vertices_with_repeated_edges(graph: Any) -> dict[int, str]:
    """Origins of edges into vertices that are not initial end vertices (only those edges run in more than one round)."""
    from checkov.common.graph.graph_builder.variable_rendering.affected_schedule import initial_end_vertices

    initial_end = initial_end_vertices(graph)
    return {edge.origin: "edge loop length changed" for edge in graph.edges if edge.dest not in initial_end}



def _digest_with_baseline_resolved(vertex: TerraformBlock, key: str, root: str, keys: list[str]) -> str:
    swap = RESOLVED_SWAPS.get(key)
    if swap is None or os.getenv("DFO_NEGATIVE", "") == "module_file_no_resolved_swap":
        return pre_render_digest(vertex, root, keys)
    current = _swap_resolved(vertex, swap[0])
    try:
        return pre_render_digest(vertex, root, keys)
    finally:
        _swap_resolved(vertex, current)


def _referrers(keys: list[str], graph: Any) -> dict[int, set[int]]:
    referrers: dict[int, set[int]] = {}
    for edge in graph.edges:
        referrers.setdefault(edge.dest, set()).add(edge.origin)
    return referrers


def affected_vertices(graph: Any, keys: list[str], artifact: dict[str, Any], root: str,
                      report: UpdateReport) -> set[int]:
    pre_render = artifact["pre_render"]
    old_digests: dict[str, str] = pre_render["digests"]
    old_edges = set(pre_render["edges"])
    del pre_render
    new_edges = {json.dumps([keys[e.origin], keys[e.dest], e.label]) for e in graph.edges}
    unconverged = set(artifact["unconverged"])
    loop_rounds_rule = _edge_loop_rounds_rule(graph, artifact, report)
    if loop_rounds_rule == "same":
        unconverged = set()
    seeds: dict[int, str] = {}
    if loop_rounds_rule == "changed":
        seeds.update(_vertices_with_repeated_edges(graph))
    exported = artifact["vertices"]
    decode = artifact.get("vertex_decoder")
    for index, (key, vertex) in enumerate(zip(keys, graph.vertices)):
        if key not in exported:
            seeds[index] = "new vertex"
        elif old_digests.get(key) != _digest_with_baseline_resolved(vertex, key, root, keys):
            seeds[index] = "pre-render state changed"
        elif key in unconverged:
            seeds[index] = "baseline render did not converge"
        elif _needs_clock_rerender(vertex, key, exported, decode):
            seeds[index] = "non-deterministic function"
    by_key = {k: i for i, k in enumerate(keys)}
    for edge in sorted(old_edges ^ new_edges):
        origin, _, _ = json.loads(edge)
        if origin in by_key:
            seeds.setdefault(by_key[origin], "outgoing edge set changed")
    removed = sorted(set(exported) - set(keys))
    report.removed_blocks = removed
    report.changed_blocks = sorted(keys[i] for i in seeds)
    removed_provider_dirs = {os.path.dirname(json.loads(k)[0].replace(ROOT, root)) for k in removed
                             if json.loads(k)[2] == BlockType.PROVIDER}
    affected = _close(graph, keys, seeds, report, removed_provider_dirs)
    for reason in seeds.values():
        report.reasons[reason] = report.reasons.get(reason, 0) + 1
    return affected


def _close(graph: Any, keys: list[str], seeds: dict[int, str], report: UpdateReport,
           removed_provider_dirs: Optional[set[str]] = None) -> set[int]:
    """Provider resolution is a lookup over the provider blocks of a resource's directory, not an edge: a provider
    that changed, appeared OR DISAPPEARED (CE-1: a removed vertex is not a seed) affects every resource there."""
    referrers = _referrers(keys, graph)
    by_block: dict[str, set[int]] = {}
    for index, key in enumerate(keys):
        by_block.setdefault(block_key(key), set()).add(index)
    provider_dirs = {os.path.dirname(graph.vertices[i].path) for i in seeds
                     if graph.vertices[i].block_type == BlockType.PROVIDER} | (removed_provider_dirs or set())
    affected = set(seeds)
    affected |= {i for i, v in enumerate(graph.vertices)
                 if v.block_type == BlockType.RESOURCE and os.path.dirname(v.path) in provider_dirs}
    stack = list(affected)
    while stack:
        index = stack.pop()
        for nxt in referrers.get(index, set()) | by_block.get(block_key(keys[index]), set()):
            if nxt not in affected:
                affected.add(nxt)
                stack.append(nxt)
    return affected


# --------------------------------------------------------------------------------------------------- restore


def restore_vertex(vertex: TerraformBlock, data: dict[str, Any], by_key: dict[str, int], root: str) -> None:
    """Copy an exported rendered state onto the PR's pre-render vertex of the same key, as it is at the END of the
    edge loop (`loop_end`: what referrers read during the loop). The final attributes / config are applied by
    restore_final_state after the loop. `by_key` holds anonymised keys (as in the artifact)."""
    loop_state = _restore(data["loop_end"], root)
    vertex.attributes = loop_state["attributes"]
    vertex.config = loop_state["config"]
    vertex.changed_attributes = {}
    for attr, crumbs in data["changed_attributes"].items():
        restored = []
        for key, attribute_key in crumbs:
            if key not in by_key:
                raise IncrementalGraphUnsupported(f"breadcrumb of frozen vertex points to a vertex gone in the PR: {key}")
            restored.append(BreadcrumbMetadata(by_key[key], attribute_key))
        vertex.changed_attributes[attr] = restored
    vertex.module_connections = {}
    for attr, ids in data["module_connections"].items():
        if any(k not in by_key for k in ids):
            raise IncrementalGraphUnsupported("module connection of frozen vertex points to a vertex gone in the PR")
        vertex.module_connections[attr] = [by_key[k] for k in ids]
    vertex.foreach_attrs = _restore(data["foreach_attrs"], root)
    vertex.dynamic_attributes = _restore(data["dynamic_attributes"], root)
    vertex.has_dynamic_block = data["has_dynamic_block"]
    vertex.breadcrumbs = {}


def update_graph(artifact: dict[str, Any], graph: Any, root: str, release: Optional[Any] = None) -> UpdateReport:
    """`graph`: the PR tree's TerraformLocalGraph after build_pre_render_graph(). Renders it incrementally in place.
    `release`: called once everything has been read from `artifact` (before the edge loop), so the caller can drop
    the serialized export while rendering runs."""
    _require_flag()
    from checkov.terraform.graph_builder.variable_rendering.renderer import TerraformVariableRenderer

    if artifact.get("version") != ARTIFACT_VERSION:
        raise IncrementalGraphUnsupported(f"artifact version {artifact.get('version')} != {ARTIFACT_VERSION}")
    root = os.path.realpath(root)
    keys = vertex_keys(graph, root)
    report = UpdateReport(vertices=len(keys))
    affected = affected_vertices(graph, keys, artifact, root, report)
    release_part = getattr(artifact, "release_part", None)
    if release_part is not None:
        release_part("pre_render")
    by_key = {k: i for i, k in enumerate(keys)}
    frozen = set()
    decode = artifact.get("vertex_decoder")
    records = artifact["vertices"]
    reread_records = _is_indexed_records(records) and reread_final_states_enabled()
    final_states: dict[int, Any] = {}
    """per frozen vertex: its exported record, kept ENCODED when the store encodes records (decoded again at the end
    of the edge loop, one vertex at a time), else the decoded record; with an indexed record file only the key is
    kept and the record is read from disk again at the end of the loop"""
    for index, key in enumerate(keys):
        if index in affected:
            continue
        stored = records[key]
        record = decode(stored) if decode is not None else stored
        restore_vertex(graph.vertices[index], record, by_key, root)
        if key in RESOLVED_SWAPS:
            _swap_resolved(graph.vertices[index], RESOLVED_SWAPS[key][1])
        final_states[index] = key if reread_records else stored
        frozen.add(index)
    report.affected, report.frozen = len(affected), len(frozen)
    artifact = {}
    if release is not None and not reread_records:
        release()
        records = None

    if os.getenv("DFO_NEGATIVE", "") == "stale_loop_end_state":
        final_states.clear()

    def restore_final_state() -> None:
        for index in sorted(final_states):
            stored = records[final_states.pop(index)] if reread_records else final_states.pop(index)
            record = decode(stored) if decode is not None else stored
            if reread_records and os.getenv("DFO_NEGATIVE", "") == "reread_final_state_as_loop_end":
                record = {**record, "attributes": record["loop_end"]["attributes"], "config": record["loop_end"]["config"]}
            graph.vertices[index].attributes = _restore(record["attributes"], root)
            graph.vertices[index].config = _restore(record["config"], root)
            if keys[index] in RESOLVED_SWAPS:
                _swap_resolved(graph.vertices[index], RESOLVED_SWAPS[keys[index]][1])
        if reread_records and release is not None:
            release()

    renderer = TerraformVariableRenderer(graph)
    renderer.frozen_vertices = frozen
    renderer.on_edge_loop_end = restore_final_state
    written: set[int] = set()
    original_update = graph.update_vertex_attribute

    def tracking_update(vertex_index: int, *args: Any, **kwargs: Any) -> Any:
        written.add(vertex_index)
        return original_update(vertex_index, *args, **kwargs)

    original_evaluate = renderer.evaluate_vertex_attribute_from_edge

    def counting_evaluate(edge_list: Any) -> Any:
        report.edges_evaluated += len(edge_list)
        return original_evaluate(edge_list)

    graph.update_vertex_attribute = tracking_update
    renderer.evaluate_vertex_attribute_from_edge = counting_evaluate
    try:
        renderer.render_variables_from_local_graph()
    finally:
        del graph.update_vertex_attribute
    report.vertices_written = len(written)
    report.frozen_written = len(written & frozen)
    report.edge_schedule = renderer.schedule_stats
    graph.update_vertices_fields()
    graph.build_post_render_edges()
    logging.info(f"[incremental graph] {report.affected} affected / {report.frozen} frozen of {report.vertices}")
    return report


# --------------------------------------------------------------------------------------------------- convergence


def unconverged_vertices(renderer: Any, graph: Any, root: str) -> set[str]:
    """Vertices with outgoing edges the render loop never completed (it stopped at its cap)."""
    keys = vertex_keys(graph, root)
    pending = set()
    for origin, edges in graph.out_edges.items():
        done = set(renderer.done_edges_by_origin_vertex.get(origin, []))
        if edges and not set(edges).issubset(done):
            pending.add(keys[origin])
    return pending
