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
    affected_indices: list[int] = field(default_factory=list)
    """PR vertex indices in the affected set (used by scoped check execution)"""
    post_render_changed_indices: list[int] = field(default_factory=list)
    """PR vertex indices that gained or lost a post-render edge"""


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


def _restore_in_place(value: Any, root: str, unmark: bool = True, as_lists: bool = False) -> Any:
    """Replacement of ROOT with `root` and unmarking of TUPLE_MARKER, avoiding json.dumps+loads round-trip.
    Creates fresh dicts/lists when copying decoded records or unshared structures."""
    if isinstance(value, str):
        return value.replace(ROOT, root) if ROOT in value else value
    if isinstance(value, dict):
        if len(value) == 1 and TUPLE_MARKER in value:
            inner = [_restore_in_place(v, root, unmark, as_lists) for v in value[TUPLE_MARKER]]
            return inner if as_lists or not unmark else tuple(inner)
        return {(k.replace(ROOT, root) if isinstance(k, str) and ROOT in k else k):
                _restore_in_place(v, root, unmark, as_lists) for k, v in value.items()}
    if isinstance(value, list):
        return [_restore_in_place(v, root, unmark, as_lists) for v in value]
    if isinstance(value, tuple):
        items = [_restore_in_place(v, root, unmark, as_lists) for v in value]
        return items if as_lists else tuple(items)
    return value


def _restore(value: Any, root: str) -> Any:
    preserve = _preserve_tuples()
    return _restore_in_place(value, root, unmark=True, as_lists=not preserve)


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
    cached_key = getattr(vertex, "dfo_key", None)
    if cached_key is not None and not PATH_RENAMES:
        return cached_key
    chain_cache: dict[tuple[str, Any], Any] = getattr(vertex_key, "_chain_cache", {})
    if not hasattr(vertex_key, "_chain_cache"):
        vertex_key._chain_cache = chain_cache  # type: ignore[attr-defined]
    ck = (root, vertex.source_module_object)
    if ck not in chain_cache:
        chain_cache[ck] = _anonymise([list(m) for m in module_chain_key(vertex.source_module_object)], root)
    v_path = vertex.path.replace(root, ROOT) if root in vertex.path else vertex.path
    identity: list[Any] = [v_path, chain_cache[ck], vertex.block_type, vertex.name, vertex.for_each_index]
    if vertex.block_type == BlockType.TF_VARIABLE:
        ldir = vertex.attributes.get("load_dir")
        identity.append(ldir.replace(root, ROOT) if isinstance(ldir, str) and root in ldir else ldir)
    return json.dumps(identity, sort_keys=True)


def block_key(key: str, vertex: Optional[Any] = None) -> str:
    """Key of the source block an (expanded) vertex comes from: instance indices removed."""
    if not key and vertex is not None:
        key = vertex_key(vertex, "")
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


def _needs_clock_rerender_by_key(key: str, exported: Any, decode: Any) -> bool:
    if not clock_evaluated_only_enabled():
        return True
    stored = exported[key]
    record = decode(stored) if decode is not None else stored
    return not _baseline_left_clock_unevaluated(record)


def _needs_clock_rerender(vertex: TerraformBlock, key: str, exported: Any, decode: Any) -> bool:
    if not uses_non_deterministic_function(vertex):
        return False
    return _needs_clock_rerender_by_key(key, exported, decode)


# --------------------------------------------------------------------------------------------------- export


def capture_pre_render(graph: Any, root: str) -> dict[str, Any]:
    """Pre-render digests and edges of a graph that has been built up to (not including) rendering."""
    keys = vertex_keys(graph, root)
    return {
        "keys": keys,
        "digests": {k: pre_render_digest(v, root, keys) for k, v in zip(keys, graph.vertices)},
        "source_modules": {k: sorted(keys[i] for i in v.source_module) for k, v in zip(keys, graph.vertices)
                           if v.source_module},
        "clock_keys": sorted(k for k, v in zip(keys, graph.vertices) if uses_non_deterministic_function(v)),
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
            "id": vertex.id,
            "source": vertex.source,
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
        "vertex_count": len(keys),
        "vertices": vertices,
        "edges": sorted(json.dumps([keys[e.origin], keys[e.dest], e.label]) for e in graph.edges),
        "cross_edges": sorted(json.dumps([keys[e.origin], keys[e.dest], e.label]) for e in graph.edges
                              if e.label.startswith("[cross-variable] ")),
        "pre_render": _anonymise(pre_render, root),
        "unconverged": sorted(unconverged),
        "edge_loop_rounds": _edge_loop_rounds(graph),
        "clock_keys": sorted(set(_anonymise(pre_render.get("clock_keys", []), root))
                             | {k for k, v in zip(keys, graph.vertices) if uses_non_deterministic_function(v)}),
        "evaluated_clock_keys": sorted(
            k for k in (set(_anonymise(pre_render.get("clock_keys", []), root))
                        | {k for k, v in zip(keys, graph.vertices) if uses_non_deterministic_function(v)})
            if not _baseline_left_clock_unevaluated(
                __import__("checkov.terraform.diff_scan.artifact_store", fromlist=["decode_record"]).decode_record(vertices[k])
                if encode is not None else vertices[k]
            )
        ),
    }


# --------------------------------------------------------------------------------------------------- affected set

UNCONVERGED_RULE_ENV = "CHECKOV_INCREMENTAL_PRECISE_UNCONVERGED"
"""Opt-in (set by the diff scan): baseline-unconverged vertices are re-rendered only if the edge loop's length changed."""


def _edge_loop_rounds(graph: Any) -> int:
    from checkov.common.graph.graph_builder.variable_rendering.affected_schedule import edge_loop_rounds
    from checkov.common.graph.graph_builder.variable_rendering.renderer import VariableRenderer

    return edge_loop_rounds(graph, VariableRenderer.MAX_NUMBER_OF_LOOPS)


def _edge_loop_rounds_rule(graph: Any, artifact: dict[str, Any], report: UpdateReport,
                           edges_unchanged: bool = False) -> str:
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
    rounds = artifact["edge_loop_rounds"] if edges_unchanged else _edge_loop_rounds(graph)
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


_LAZY_SM_UNSET = object()


def affected_vertices(graph: Any, keys: list[str], artifact: dict[str, Any], root: str,
                      report: UpdateReport) -> set[int]:
    edges_fast = bool(
        getattr(graph, "dfo_pre_render_edges_unchanged", False)
        and len(keys) == int(artifact.get("vertex_count", -1))
    )
    non_reused = [
        i for i, (k, v) in enumerate(zip(keys, graph.vertices))
        if not getattr(v, "dfo_reused_unchanged", False)
        or k in RESOLVED_SWAPS
        or (getattr(v, "dfo_baseline_sm_indices", _LAZY_SM_UNSET) != v.source_module
            and {keys[j] for j in v.source_module} != (getattr(v, "dfo_baseline_source_module", None) or set()))
    ]
    if edges_fast and hasattr(artifact, "_artifact") and "clock_keys" in artifact and not non_reused:
        old_clock_keys: Optional[set[str]] = set(artifact["clock_keys"])
        old_source_modules: Optional[dict[str, list[str]]] = None
        old_digests: dict[str, str] = {}
        old_edges_list: list[str] = []
        exported: Any = None
    elif edges_fast and hasattr(artifact, "_artifact") and "clock_keys" in artifact:
        old_clock_keys = set(artifact["clock_keys"])
        old_source_modules = None
        old_digests = dict(getattr(graph, "dfo_pre_render_digests", None) or {})
        if not all(keys[i] in old_digests for i in non_reused):
            pre_render = artifact["pre_render"]
            old_digests = {keys[i]: pre_render["digests"].get(keys[i], "") for i in non_reused}
            del pre_render
            release_part = getattr(artifact, "release_part", None)
            if release_part is not None:
                release_part("pre_render")
        old_edges_list = []
        exported = None if all(keys[i] in old_digests for i in non_reused) else artifact["vertices"]
    else:
        pre_render = artifact["pre_render"]
        old_edges_list = [] if edges_fast else pre_render.pop("edges", [])
        old_digests = {keys[i]: pre_render["digests"][keys[i]] for i in non_reused if keys[i] in pre_render["digests"]}
        old_source_modules = None
        old_clock_keys = set(pre_render["clock_keys"]) if "clock_keys" in pre_render else None
        edges_fast = edges_fast and len(keys) == len(pre_render["digests"])
        if os.getenv("DFO_NEGATIVE", "") != "rename_no_digest_backmap":
            pre_render.clear()
        del pre_render
        if os.getenv("DFO_NEGATIVE", "") != "rename_no_digest_backmap":
            release_part = getattr(artifact, "release_part", None)
            if release_part is not None:
                release_part("pre_render")
        import gc
        gc.collect()
        exported = artifact["vertices"]
    seeds: dict[int, str] = {}
    edge_diff_endpoints: set[int] = set()
    if edges_fast:
        edges_unchanged = True
    else:
        by_key = {k: i for i, k in enumerate(keys)}
        old_edges = set(old_edges_list)
        del old_edges_list
        import gc
        gc.collect()
        seen_new_edges: set[str] = set()
        added_edges = False
        for e in graph.edges:
            edge_str = json.dumps([keys[e.origin], keys[e.dest], e.label])
            if edge_str in old_edges:
                old_edges.discard(edge_str)
                seen_new_edges.add(edge_str)
            elif edge_str not in seen_new_edges:
                seen_new_edges.add(edge_str)
                added_edges = True
                seeds.setdefault(e.origin, "outgoing edge set changed")
                edge_diff_endpoints.add(e.origin)
                edge_diff_endpoints.add(e.dest)
        del seen_new_edges
        edges_unchanged = not added_edges and not old_edges
        for edge in sorted(old_edges):
            origin, dest_k, _ = json.loads(edge)
            if origin in by_key:
                seeds.setdefault(by_key[origin], "outgoing edge set changed")
                edge_diff_endpoints.add(by_key[origin])
            if dest_k in by_key:
                edge_diff_endpoints.add(by_key[dest_k])
        del old_edges, by_key
        gc.collect()
    unconverged = set(artifact["unconverged"])
    loop_rounds_rule = _edge_loop_rounds_rule(graph, artifact, report, edges_unchanged=edges_unchanged)
    if loop_rounds_rule == "same":
        unconverged = set()
    if loop_rounds_rule == "changed":
        for idx, r_reason in _vertices_with_repeated_edges(graph).items():
            seeds[idx] = r_reason
    decode = artifact.get("vertex_decoder")
    for index, (key, vertex) in enumerate(zip(keys, graph.vertices)):
        if exported is not None and key not in exported:
            seeds[index] = "new vertex"
            continue
        if getattr(vertex, "dfo_reused_unchanged", False) and key not in RESOLVED_SWAPS \
                and (getattr(vertex, "dfo_baseline_sm_indices", _LAZY_SM_UNSET) == vertex.source_module
                     or {keys[i] for i in vertex.source_module} == (getattr(vertex, "dfo_baseline_source_module", None) or set())) \
                and os.getenv("DFO_NEGATIVE", "") != "rename_no_digest_backmap":
            if key in unconverged:
                seeds[index] = "baseline render did not converge"
            elif (key in old_clock_keys if old_clock_keys is not None else False):
                if exported is None:
                    exported = artifact["vertices"]
                if _needs_clock_rerender_by_key(key, exported, decode):
                    seeds[index] = "non-deterministic function"
            continue
        if os.getenv("DFO_NEGATIVE", "") == "rename_no_digest_backmap" and not old_digests and "pre_render" in artifact:
            old_digests = artifact["pre_render"]["digests"]
        if getattr(vertex, "_loader", None) is not None and not getattr(vertex, "_loaded", True):
            vertex._ensure_loaded()
        if old_digests.get(key) != _digest_with_baseline_resolved(vertex, key, root, keys):
            seeds[index] = "pre-render state changed"
        elif key in unconverged:
            seeds[index] = "baseline render did not converge"
        else:
            if exported is None and uses_non_deterministic_function(vertex):
                exported = artifact["vertices"]
            if exported is not None and _needs_clock_rerender(vertex, key, exported, decode):
                seeds[index] = "non-deterministic function"
    del old_digests
    del old_source_modules
    removed = [] if (edges_fast and exported is None) else sorted(set(exported) - set(keys))
    report.removed_blocks = removed
    report.changed_blocks = sorted(keys[i] for i in seeds)
    removed_provider_dirs = {os.path.dirname(json.loads(k)[0].replace(ROOT, root)) for k in removed
                             if json.loads(k)[2] == BlockType.PROVIDER}
    affected, provider_seed_indices = _close(graph, keys, seeds, report, removed_provider_dirs, return_provider_seeds=True)
    for reason in seeds.values():
        report.reasons[reason] = report.reasons.get(reason, 0) + 1
    report.edge_diff_origins = edge_diff_endpoints | provider_seed_indices  # type: ignore[attr-defined]
    report.provider_seed_indices = provider_seed_indices  # type: ignore[attr-defined]
    return affected


def _close(graph: Any, keys: list[str], seeds: dict[int, str], report: UpdateReport,
           removed_provider_dirs: Optional[set[str]] = None,
           return_provider_seeds: bool = False, root: str = "") -> Any:
    """Provider resolution is a lookup over the provider blocks of a resource's directory, not an edge: a provider
    that changed, appeared OR DISAPPEARED (CE-1: a removed vertex is not a seed) affects every resource there."""
    provider_dirs = {os.path.dirname(graph.vertices[i].path) for i in seeds
                     if graph.vertices[i].block_type == BlockType.PROVIDER} | (removed_provider_dirs or set())
    affected = set(seeds)
    provider_resources: set[int] = set()
    if provider_dirs:
        affected |= {i for i, v in enumerate(graph.vertices)
                     if v.block_type == BlockType.RESOURCE and os.path.dirname(v.path) in provider_dirs}
        p_mod_callers: set[int] = {
            i for i, v in enumerate(graph.vertices)
            if v.block_type == BlockType.MODULE and os.path.dirname(v.path) in provider_dirs
        }
        p_stack = list(p_mod_callers)
        while p_stack:
            m_cur = p_stack.pop()
            for i, v in enumerate(graph.vertices):
                if m_cur in v.source_module and v.block_type == BlockType.MODULE and i not in p_mod_callers:
                    p_mod_callers.add(i)
                    p_stack.append(i)
        provider_resources = {
            i for i, v in enumerate(graph.vertices)
            if v.block_type == BlockType.RESOURCE and (
                os.path.dirname(v.path) in provider_dirs or bool(v.source_module & p_mod_callers)
            )
        }
    if not affected:
        return (affected, provider_resources) if return_provider_seeds else affected
    by_block: dict[Any, set[int]] = {}
    counted_bases: set[tuple[str, str, str]] = set()
    for index, v in enumerate(graph.vertices):
        if "[" in v.name or v.for_each_index is not None:
            counted_bases.add((v.path, v.block_type, v.name.split("[", 1)[0]))
    if counted_bases:
        for index, v in enumerate(graph.vertices):
            base_tuple = (v.path, v.block_type, v.name.split("[", 1)[0])
            if base_tuple in counted_bases:
                by_block.setdefault((v.path, v.source_module_object, v.block_type, base_tuple[2]), set()).add(index)
    stack = list(affected)
    while stack:
        index = stack.pop()
        in_referrers = {e.origin for e in graph.in_edges.get(index, ())}
        v_cur = graph.vertices[index]
        block_siblings = by_block.get(
            (v_cur.path, v_cur.source_module_object, v_cur.block_type, v_cur.name.split("[", 1)[0]), set()
        ) if by_block else set()
        for nxt in in_referrers | block_siblings:
            if nxt not in affected:
                affected.add(nxt)
                stack.append(nxt)
    return (affected, provider_resources) if return_provider_seeds else affected


# --------------------------------------------------------------------------------------------------- restore


def _resolve_key_in_graph(key: str, graph: Any, root: str, cache: dict[str, int]) -> Optional[int]:
    if key in cache:
        return cache[key]
    by_k = getattr(graph, "_dfo_by_key", None)
    if by_k is not None:
        return by_k.get(key)
    ident = json.loads(key)
    v_path = ident[0].replace(ROOT, root)
    if not os.path.isabs(v_path) or ROOT in ident[0] and not v_path.startswith(root):
        v_path = os.path.join(root, ident[0].split(ROOT + "/", 1)[-1])
    v_type, v_name = ident[2], ident[3]
    p_idx_map = getattr(graph, "_dfo_path_index", None)
    if p_idx_map is None:
        graph.__dict__.pop("_dfo_group_keys", None)
        p_idx_map = {}
        for idx, v in enumerate(graph.vertices):
            p_idx_map.setdefault(v.path, []).append(idx)
        graph._dfo_path_index = p_idx_map
    candidates = p_idx_map.get(v_path)
    if candidates is None:
        rel_s = ident[0].split(ROOT + "/", 1)[-1]
        for k_p, c_list in p_idx_map.items():
            if k_p.endswith("/" + rel_s) or k_p == rel_s:
                candidates = c_list
                break
    if candidates is None:
        return None
    if isinstance(candidates, list):
        by_tn: dict[tuple[str, str], list[int]] = {}
        for idx in candidates:
            v = graph.vertices[idx]
            by_tn.setdefault((v.block_type, v.name), []).append(idx)
            if v.block_type == BlockType.MODULE and "[" in v.name:
                by_tn.setdefault((v.block_type, v.name.split("[", 1)[0]), []).append(idx)
        p_idx_map[v_path] = by_tn
        candidates = by_tn
    lookup_name = v_name.split("[", 1)[0] if v_type == BlockType.MODULE and "[" in v_name else v_name
    group = (v_type, lookup_name)
    if group_key_cache_enabled():
        return _keys_of_group(graph, candidates, v_path, group, root).get(key)
    for idx in candidates.get(group, ()):
        v = graph.vertices[idx]
        k_idx = vertex_key(v, root)
        cache[k_idx] = idx
        if k_idx == key:
            return idx
    return None


GROUP_KEY_CACHE_ENV = "CHECKOV_DIFF_GROUP_KEY_CACHE"
"""Opt-in: the keys of a (path, block type, name) candidate group are computed once per graph. Without it every
lookup recomputes the keys of the group's vertices up to the match: a module file instantiated N times gives N
vertices of the same (path, type, name), so N lookups cost O(N^2) key computations."""


def group_key_cache_enabled() -> bool:
    return os.getenv(GROUP_KEY_CACHE_ENV, "false").lower() == "true"


def _keys_of_group(graph: Any, candidates: dict[tuple[str, str], list[int]], v_path: str, group: tuple[str, str],
                   root: str) -> dict[str, int]:
    """key -> vertex index for one candidate group; the first index wins on equal keys (the uncached loop returns the
    first match in candidate order)."""
    cache: dict[tuple[str, tuple[str, str]], dict[str, int]] = graph.__dict__.setdefault("_dfo_group_keys", {})
    keys = cache.get((v_path, group))
    if keys is None:
        keys = {}
        for idx in candidates.get(group, ()):
            keys.setdefault(vertex_key(graph.vertices[idx], root), idx)
        cache[(v_path, group)] = keys
    return keys


def restore_vertex(vertex: TerraformBlock, data: dict[str, Any], by_key: dict[str, int], root: str,
                   skip_loop_end: bool = False, graph: Any = None) -> None:
    """Copy an exported rendered state onto the PR's pre-render vertex of the same key, as it is at the END of the
    edge loop (`loop_end`: what referrers read during the loop). The final attributes / config are applied by
    restore_final_state after the loop. `by_key` holds anonymised keys (as in the artifact)."""
    if not skip_loop_end:
        loop_state = _restore(data["loop_end"], root)
        vertex.attributes = loop_state["attributes"]
        vertex.config = loop_state["config"]
    vertex.changed_attributes = {}
    for attr, crumbs in data["changed_attributes"].items():
        restored = []
        for key, attribute_key in crumbs:
            target_idx = by_key.get(key)
            if target_idx is None and graph is not None:
                target_idx = _resolve_key_in_graph(key, graph, root, by_key)
            if target_idx is None:
                raise IncrementalGraphUnsupported(f"breadcrumb of frozen vertex points to a vertex gone in the PR: {key}")
            restored.append(BreadcrumbMetadata(target_idx, attribute_key))
        vertex.changed_attributes[attr] = restored
    vertex.module_connections = {}
    for attr, ids in data["module_connections"].items():
        resolved_ids = []
        for k in ids:
            t_idx = by_key.get(k)
            if t_idx is None and graph is not None:
                t_idx = _resolve_key_in_graph(k, graph, root, by_key)
            if t_idx is None:
                raise IncrementalGraphUnsupported("module connection of frozen vertex points to a vertex gone in the PR")
            resolved_ids.append(t_idx)
        vertex.module_connections[attr] = resolved_ids
    vertex.foreach_attrs = _restore(data["foreach_attrs"], root)
    vertex.dynamic_attributes = _restore(data["dynamic_attributes"], root)
    vertex.has_dynamic_block = data["has_dynamic_block"]
    vertex.breadcrumbs = {}
    mark = getattr(vertex, "mark_restored", None)
    if mark is not None:
        default_id = vertex.name if vertex.block_type in (BlockType.RESOURCE, BlockType.DATA) else ""
        mark(data.get("id", default_id), data.get("source", "Terraform"))


def update_graph(artifact: dict[str, Any], graph: Any, root: str, release: Optional[Any] = None) -> UpdateReport:
    """`graph`: the PR tree's TerraformLocalGraph after build_pre_render_graph(). Renders it incrementally in place.
    `release`: called once everything has been read from `artifact` (before the edge loop), so the caller can drop
    the serialized export while rendering runs."""
    _require_flag()
    from checkov.terraform.graph_builder.variable_rendering.renderer import TerraformVariableRenderer

    if artifact.get("version") != ARTIFACT_VERSION:
        raise IncrementalGraphUnsupported(f"artifact version {artifact.get('version')} != {ARTIFACT_VERSION}")
    root = os.path.realpath(root)
    edges_fast_pre = bool(
        (getattr(graph, "dfo_pre_render_edges_unchanged", False)
         or (getattr(graph, "dfo_replayed_edges_unchanged", False) and hasattr(graph, "dfo_pre_render_digests")))
        and hasattr(artifact, "_artifact") and "clock_keys" in artifact
        and not RESOLVED_SWAPS
        and os.getenv("DFO_NEGATIVE", "") != "rename_no_digest_backmap"
    )
    if edges_fast_pre:
        keys: list[str] = []
        report = UpdateReport(vertices=len(graph.vertices))
        report.removed_blocks = sorted(getattr(graph, "dfo_removed_keys", None) or [])
        removed_provider_dirs_pre = {
            os.path.dirname(json.loads(k)[0].replace(ROOT, root)) for k in report.removed_blocks
            if json.loads(k)[2] == BlockType.PROVIDER
        }
        old_clock_keys_pre = set(artifact["clock_keys"])
        old_eval_clock_pre = set(artifact["evaluated_clock_keys"]) if "evaluated_clock_keys" in artifact else None
        old_digests_pre = getattr(graph, "dfo_pre_render_digests", None)
        if old_digests_pre is None:
            pre_r = artifact["pre_render"]
            old_digests_pre = pre_r.pop("digests", {})
            pre_r.clear()
            del pre_r
            rel_p = getattr(artifact, "release_part", None)
            if rel_p is not None:
                rel_p("pre_render")
            import gc
            gc.collect()
        else:
            old_digests_pre = dict(old_digests_pre)
        seeds_pre: dict[int, str] = {}
        if not getattr(graph, "dfo_pre_render_edges_unchanged", False) \
                and getattr(graph, "dfo_replayed_edges_unchanged", False):
            rebuilt_offs = list(getattr(graph, "dfo_rebuilt_unit_offsets", ()) or ())
            extra_edge_seeds: dict[int, str] = {}
            extra_edge_endpoints: set[int] = set()
            old_u_edges = set(getattr(graph, "dfo_old_touched_edges", ()) or ())
            new_u_edges: set[tuple[str, str, str]] = set()
            for off_s, off_e in rebuilt_offs:
                for idx_v in range(off_s, off_e):
                    ok_v = vertex_key(graph.vertices[idx_v], root)
                    for e_v in graph.out_edges.get(idx_v, ()):
                        dk_v = vertex_key(graph.vertices[e_v.dest], root)
                        et = (ok_v, dk_v, e_v.label)
                        new_u_edges.add(et)
                        if et not in old_u_edges:
                            extra_edge_seeds.setdefault(e_v.origin, "outgoing edge set changed")
                            extra_edge_endpoints.add(e_v.origin)
                            extra_edge_endpoints.add(e_v.dest)
            unit_key_to_pr = getattr(graph, "_dfo_unit_key_to_pr", None) or {}
            for ok_v, dk_v, _ in old_u_edges - new_u_edges:
                if ok_v in unit_key_to_pr:
                    extra_edge_seeds.setdefault(unit_key_to_pr[ok_v], "outgoing edge set changed")
                    extra_edge_endpoints.add(unit_key_to_pr[ok_v])
                if dk_v in unit_key_to_pr:
                    extra_edge_endpoints.add(unit_key_to_pr[dk_v])
            for idx_s, r_s in extra_edge_seeds.items():
                seeds_pre.setdefault(idx_s, r_s)
            graph.dfo_extra_edge_seeds = extra_edge_seeds  # type: ignore[attr-defined]
            graph.dfo_extra_edge_endpoints = extra_edge_endpoints  # type: ignore[attr-defined]
            graph.dfo_old_touched_edges = None  # type: ignore[attr-defined]
            del old_u_edges, new_u_edges
        loop_rule_pre = _edge_loop_rounds_rule(
            graph, artifact, report, edges_unchanged=bool(
                getattr(graph, "dfo_pre_render_edges_unchanged", False)
                or (getattr(graph, "dfo_replayed_edges_unchanged", False)
                    and not getattr(graph, "dfo_extra_edge_seeds", None)
                    and not getattr(graph, "dfo_extra_edge_endpoints", None))
            )
        )
        unconverged_pre = set() if loop_rule_pre == "same" else set(artifact["unconverged"])
        if loop_rule_pre == "changed":
            for idx_r, r_reason in _vertices_with_repeated_edges(graph).items():
                seeds_pre[idx_r] = r_reason
        decode_pre = artifact.get("vertex_decoder")
        exported_pre: Any = None
        fallback_full = False
        for index, vertex in enumerate(graph.vertices):
            if getattr(vertex, "dfo_reused_unchanged", False) \
                    and (getattr(vertex, "dfo_baseline_sm_indices", _LAZY_SM_UNSET) == vertex.source_module
                         or (not vertex.source_module and not getattr(vertex, "dfo_baseline_source_module", None))
                         or {vertex_key(graph.vertices[i], root) for i in vertex.source_module}
                         == (getattr(vertex, "dfo_baseline_source_module", None) or set())) \
                    and os.getenv("DFO_NEGATIVE", "") != "rename_no_digest_backmap":
                continue
            k_i = vertex_key(vertex, root)
            if k_i not in old_digests_pre:
                seeds_pre[index] = "new vertex"
                continue
            if getattr(vertex, "_loader", None) is not None and not getattr(vertex, "_loaded", True):
                vertex._ensure_loaded()
            source_mod_keys = sorted(vertex_key(graph.vertices[i], root) for i in vertex.source_module)
            payload = {"attributes": vertex.attributes, "config": vertex.config, "source_module": source_mod_keys,
                       "foreach_attrs": getattr(vertex, "foreach_attrs", None)}
            text = json.dumps(_anonymise(payload, root), sort_keys=True)
            for old_p, new_p in PATH_RENAMES:
                text = text.replace(new_p, old_p)
            if old_digests_pre.get(k_i) != hashlib.sha256(text.encode()).hexdigest():
                seeds_pre[index] = "pre-render state changed"
            elif k_i in unconverged_pre:
                seeds_pre[index] = "baseline render did not converge"
            elif uses_non_deterministic_function(vertex):
                if old_eval_clock_pre is not None and clock_evaluated_only_enabled() \
                        and os.getenv("DFO_NEGATIVE", "") != "clock_rule_ignores_evaluation":
                    if k_i in old_eval_clock_pre or k_i not in old_clock_keys_pre:
                        seeds_pre[index] = "non-deterministic function"
                else:
                    if exported_pre is None:
                        exported_pre = artifact["vertices"]
                    if _needs_clock_rerender(vertex, k_i, exported_pre, decode_pre):
                        seeds_pre[index] = "non-deterministic function"
        del old_digests_pre
        if not fallback_full and old_clock_keys_pre:
            use_eval_set = (
                old_eval_clock_pre is not None
                and clock_evaluated_only_enabled()
                and os.getenv("DFO_NEGATIVE", "") != "clock_rule_ignores_evaluation"
            )
            target_clock_keys = old_eval_clock_pre if use_eval_set else old_clock_keys_pre
            clock_rel_names = {
                (json.loads(ck)[0].split(ROOT + "/", 1)[-1], json.loads(ck)[3].split("[", 1)[0])
                for ck in target_clock_keys
            }
            for index, vertex in enumerate(graph.vertices):
                if index in seeds_pre or not any(
                    vertex.path.endswith(r_p) and vertex.name.split("[", 1)[0] == r_n
                    for r_p, r_n in clock_rel_names
                ):
                    continue
                k_i = vertex_key(vertex, root)
                if k_i in target_clock_keys:
                    if use_eval_set:
                        seeds_pre[index] = "non-deterministic function"
                    else:
                        if exported_pre is None:
                            exported_pre = artifact["vertices"]
                        if _needs_clock_rerender_by_key(k_i, exported_pre, decode_pre):
                            seeds_pre[index] = "non-deterministic function"
            exported_pre = None
        if not fallback_full and unconverged_pre:
            unconv_rel_names = {
                (json.loads(uk)[0].split(ROOT + "/", 1)[-1], json.loads(uk)[3].split("[", 1)[0])
                for uk in unconverged_pre
            }
            for index, vertex in enumerate(graph.vertices):
                if index in seeds_pre or not any(
                    vertex.path.endswith(r_p) and vertex.name.split("[", 1)[0] == r_n
                    for r_p, r_n in unconv_rel_names
                ):
                    continue
                k_i = vertex_key(vertex, root)
                if k_i in unconverged_pre:
                    seeds_pre[index] = "baseline render did not converge"
        if not fallback_full and os.getenv("DFO_NEGATIVE", "") != "rename_no_digest_backmap":
            report.changed_blocks = sorted(vertex_key(graph.vertices[i], root) for i in seeds_pre)
            for reason in seeds_pre.values():
                report.reasons[reason] = report.reasons.get(reason, 0) + 1
            affected, provider_seed_indices = _close(
                graph, keys, seeds_pre, report, removed_provider_dirs_pre, return_provider_seeds=True, root=root
            )
            vertex_key._chain_cache = {}  # type: ignore[attr-defined]
            report.edge_diff_origins = set(provider_seed_indices) | set(getattr(graph, "dfo_extra_edge_endpoints", None) or ())  # type: ignore[attr-defined]
            report.provider_seed_indices = set(provider_seed_indices)  # type: ignore[attr-defined]
            graph.dfo_pre_render_digests = None  # type: ignore[attr-defined]
            graph.dfo_extra_edge_seeds = None  # type: ignore[attr-defined]
            graph.dfo_extra_edge_endpoints = None  # type: ignore[attr-defined]
        else:
            keys = vertex_keys(graph, root)
            affected = affected_vertices(graph, keys, artifact, root, report)
            graph._dfo_used_full_affected = True  # type: ignore[attr-defined]
    else:
        keys = vertex_keys(graph, root)
        report = UpdateReport(vertices=len(keys))
        affected = affected_vertices(graph, keys, artifact, root, report)
        graph._dfo_used_full_affected = True  # type: ignore[attr-defined]
    release_part = getattr(artifact, "release_part", None)
    if release_part is not None:
        release_part("pre_render")
    by_key: Optional[dict[str, int]] = None
    frozen = set()
    decode = artifact.get("vertex_decoder")
    records: Any = None
    reread_records = (hasattr(artifact, "_artifact") or _is_indexed_records(artifact.get("vertices"))) and reread_final_states_enabled()
    final_states: dict[int, Any] = {}
    """per frozen vertex: its exported record, kept ENCODED when the store encodes records (decoded again at the end
    of the edge loop, one vertex at a time), else the decoded record; with an indexed record file only the key is
    kept and the record is read from disk again at the end of the loop"""
    provider_affected = getattr(report, "provider_seed_indices", set())
    for index in affected:
        if getattr(graph.vertices[index], "_loader", None) is not None and not getattr(graph.vertices[index], "_loaded", True):
            graph.vertices[index]._ensure_loaded()
    affected_mod_callers = {
        i for i in affected
        if graph.vertices[i].block_type == BlockType.MODULE and "providers" in (graph.vertices[i].attributes or {})
    }
    if affected_mod_callers:
        mod_provider_resources: set[int] = set()
        mod_stack = list(affected_mod_callers)
        mod_seen = set(affected_mod_callers)
        while mod_stack:
            m_cur = mod_stack.pop()
            for i, v in enumerate(graph.vertices):
                if m_cur in v.source_module:
                    if v.block_type == BlockType.RESOURCE:
                        mod_provider_resources.add(i)
                    elif v.block_type == BlockType.MODULE and i not in mod_seen:
                        mod_seen.add(i)
                        mod_stack.append(i)
        provider_affected = set(provider_affected) | mod_provider_resources
        report.edge_diff_origins = set(getattr(report, "edge_diff_origins", set())) | mod_provider_resources  # type: ignore[attr-defined]
    loop_read_frozen: set[int] = set()
    for index in affected:
        for e in graph.out_edges.get(index, ()):
            if e.dest not in affected:
                loop_read_frozen.add(e.dest)
        for v in graph.vertices[index].changed_attributes.values():
            for crumb in v:
                if crumb.vertex_id not in affected:
                    loop_read_frozen.add(crumb.vertex_id)
    for index, v_chk in enumerate(graph.vertices):
        if index not in affected and type(v_chk).__name__ != "LazyTerraformBlock":
            for v in v_chk.changed_attributes.values():
                for crumb in v:
                    if crumb.vertex_id not in affected:
                        loop_read_frozen.add(crumb.vertex_id)
    if RESOLVED_SWAPS:
        for index, key in enumerate(keys):
            if index not in affected and key in RESOLVED_SWAPS:
                loop_read_frozen.add(index)
    skip_loop_end = reread_records and os.getenv("DFO_NEGATIVE", "") != "stale_loop_end_state"
    lazy_final = skip_loop_end and os.getenv("CHECKOV_INCREMENTAL_LAZY_FINAL_STATE", "false").lower() == "true" \
        and os.getenv("DFO_NEGATIVE", "") != "provider_pass_aborts"
    if not lazy_final:
        if not keys:
            keys = vertex_keys(graph, root)
        by_key = {k: i for i, k in enumerate(keys)}
    graph._dfo_keys = keys if keys else None  # type: ignore[attr-defined]
    graph._dfo_by_key = by_key  # type: ignore[attr-defined]
    graph._dfo_lazy_final_loader = (artifact, decode, root) if lazy_final else None  # type: ignore[attr-defined]
    graph._dfo_provider_seeds = provider_affected  # type: ignore[attr-defined]
    graph._dfo_loop_read = loop_read_frozen  # type: ignore[attr-defined]
    for index in range(len(graph.vertices)):
        if index in affected:
            continue
        frozen.add(index)
        if skip_loop_end and index not in loop_read_frozen:
            if lazy_final and type(graph.vertices[index]).__name__ == "LazyTerraformBlock":
                graph.vertices[index]._loaded = False
                graph.vertices[index]._loader = None
                graph.vertices[index]._rendered_loader = graph
            else:
                final_states[index] = keys[index] if keys else vertex_key(graph.vertices[index], root)
            continue
        key = keys[index] if keys else vertex_key(graph.vertices[index], root)
        if records is None:
            records = artifact["vertices"]
        stored = records[key]
        record = decode(stored) if decode is not None else stored
        map_for_v: dict[str, int] = by_key if by_key is not None else getattr(graph, "_dfo_unit_key_to_pr", None)
        if map_for_v is None:
            map_for_v = {}
            graph._dfo_unit_key_to_pr = map_for_v
        restore_vertex(graph.vertices[index], record, map_for_v, root, graph=graph)
        if key in RESOLVED_SWAPS:
            _swap_resolved(graph.vertices[index], RESOLVED_SWAPS[key][1])
        final_states[index] = key if reread_records else stored
    if reread_records and lazy_final and records is not None:
        records = None
    report.affected, report.frozen = len(affected), len(frozen)
    report.affected_indices = sorted(affected)
    artifact_view = artifact
    artifact = {}
    if release is not None and not reread_records:
        release()
        records = None

    if os.getenv("DFO_NEGATIVE", "") in (
        "stale_loop_end_state", "reread_final_state_as_loop_end", "indexed_records_off_by_one",
        "lazy_vertex_wrong_record", "export_drops_tuples", "missing_section_file",
    ):
        if os.getenv("DFO_NEGATIVE", "") == "missing_section_file":
            _ = artifact_view["vertices"]
        if os.getenv("DFO_NEGATIVE", "") == "stale_loop_end_state":
            final_states.clear()
        for v in graph.vertices:
            if getattr(v, "_rendered_loader", None) is not None:
                if os.getenv("DFO_NEGATIVE", "") in ("lazy_vertex_wrong_record", "export_drops_tuples", "indexed_records_off_by_one", "reread_final_state_as_loop_end"):
                    v._ensure_loaded()
                else:
                    v._ensure_loaded_loop_end()

    def restore_final_state() -> None:
        nonlocal records, by_key
        skip_loop_end = reread_records and os.getenv("DFO_NEGATIVE", "") != "stale_loop_end_state"
        for index in sorted(final_states):
            stored_or_key = final_states.pop(index)
            vertex = graph.vertices[index]
            if lazy_final and index not in loop_read_frozen and type(vertex).__name__ == "LazyTerraformBlock":
                continue
            if reread_records and records is None:
                records = artifact_view["vertices"]
            stored = records[stored_or_key] if reread_records else stored_or_key
            record = decode(stored) if decode is not None else stored
            if reread_records and os.getenv("DFO_NEGATIVE", "") == "reread_final_state_as_loop_end":
                record = {**record, "attributes": record["loop_end"]["attributes"], "config": record["loop_end"]["config"]}
            if skip_loop_end and index not in loop_read_frozen:
                map_for_v2: dict[str, int] = by_key if by_key is not None else getattr(graph, "_dfo_unit_key_to_pr", None)
                if map_for_v2 is None:
                    map_for_v2 = {}
                    graph._dfo_unit_key_to_pr = map_for_v2
                restore_vertex(vertex, record, map_for_v2, root, skip_loop_end=True, graph=graph)
            vertex.attributes = _restore(record["attributes"], root)
            vertex.config = _restore(record["config"], root)
            vertex.attributes = _restore(record["attributes"], root)
            vertex.config = _restore(record["config"], root)
            if isinstance(vertex.config, dict) and vertex.block_type == BlockType.RESOURCE:
                for r_val in vertex.config.values():
                    if isinstance(r_val, dict):
                        for e_cfg in r_val.values():
                            if isinstance(e_cfg, dict) and isinstance(e_cfg.get("__start_line__"), list) \
                                    and isinstance(e_cfg.get("__end_line__"), list):
                                e_cfg["__start_line__"] = e_cfg["__start_line__"][0]
                                e_cfg["__end_line__"] = e_cfg["__end_line__"][0]
            if os.getenv("DFO_NEGATIVE", "") == "provider_pass_aborts" and vertex.block_type == BlockType.RESOURCE:
                from checkov.common.graph.graph_builder import CustomAttributes
                vertex.attributes.pop(CustomAttributes.PROVIDER_ADDRESS, None)
                v_name = vertex.name.split(".")
                if len(v_name) >= 2 and isinstance(vertex.config.get(v_name[0], {}).get(v_name[1]), dict):
                    vertex.config[v_name[0]][v_name[1]].pop(CustomAttributes.PROVIDER_ADDRESS, None)
            if RESOLVED_SWAPS:
                k_i = keys[index] if keys else vertex_key(vertex, root)
                if k_i in RESOLVED_SWAPS:
                    _swap_resolved(vertex, RESOLVED_SWAPS[k_i][1])
        if reread_records and release is not None and not lazy_final:
            release()
        elif reread_records and lazy_final:
            records = None

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
    del frozen, renderer, written
    if lazy_final and "edges" in artifact_view and os.getenv("DFO_NEGATIVE", "") != "provider_pass_aborts":
        post_changed = _finish_with_lazy_frozen(graph, keys, by_key, affected, artifact_view, lazy_final, root)
        post_changed |= getattr(report, "edge_diff_origins", set())
        report.post_render_changed_indices = sorted(post_changed)
    else:
        if not graph.vertices_by_module_dependency_by_name:
            graph.vertices_by_block_type.clear()
            graph.vertices_by_module_dependency.clear()
            for idx, b in enumerate(graph.vertices):
                graph.out_edges.setdefault(idx, [])
                graph.in_edges.setdefault(idx, [])
                graph.vertices_by_block_type[b.block_type].append(idx)
                graph.vertices_block_name_map[b.block_type][b.name].append(idx)
                if b.block_type == BlockType.MODULE:
                    graph.map_path_to_module.setdefault(b.path, []).append(idx)
                graph.vertices_by_module_dependency[b.source_module_object][b.block_type].append(idx)
                graph.vertices_by_module_dependency_by_name[b.source_module_object][b.block_type][b.name].append(idx)
        for v in graph.vertices:
            if getattr(v, "_rendered_loader", None) is not None:
                v._ensure_loaded()
            if os.getenv("DFO_NEGATIVE", "") == "provider_pass_aborts" and v.block_type == BlockType.RESOURCE:
                from checkov.common.graph.graph_builder import CustomAttributes
                v.attributes.pop(CustomAttributes.PROVIDER_ADDRESS, None)
                v_name = v.name.split(".")
                if len(v_name) >= 2 and isinstance(v.config.get(v_name[0], {}).get(v_name[1]), dict):
                    v.config[v_name[0]][v_name[1]].pop(CustomAttributes.PROVIDER_ADDRESS, None)
        old_all_edges = {tuple(json.loads(e)) for e in artifact_view.get("edges", [])}
        release_part = getattr(artifact_view, "release_part", None)
        if release_part is not None:
            release_part("edges")
        graph.update_vertices_fields()
        graph.build_post_render_edges()
        if not keys:
            keys[:] = vertex_keys(graph, root)
        new_all_edges = {(keys[e.origin], keys[e.dest], e.label) for e in graph.edges}
        changed_edge_indices: set[int] = set()
        if by_key is None:
            by_key = {k: i for i, k in enumerate(keys)}
        for ok, dk, _ in old_all_edges ^ new_all_edges:
            if ok in by_key:
                changed_edge_indices.add(by_key[ok])
            if dk in by_key:
                changed_edge_indices.add(by_key[dk])
        report.post_render_changed_indices = sorted(changed_edge_indices)
    if os.getenv("CHECKOV_INCREMENTAL_LAZY_FINAL_STATE", "false").lower() == "true":
        vertex_key._chain_cache = {}  # type: ignore[attr-defined]
        graph._dfo_path_index = None  # type: ignore[attr-defined]
        graph.__dict__.pop("_dfo_group_keys", None)
    logging.info(f"[incremental graph] {report.affected} affected / {report.frozen} frozen of {report.vertices}")
    return report


# --------------------------------------------------------------------------------------------------- convergence


def _finish_with_lazy_frozen(graph: Any, keys: list[str], by_key: Optional[dict[str, int]], affected: set[int],
                             artifact_view: Any, lazy_final: bool = True, root: str = "") -> set[int]:
    """Run update_vertices_fields and build_post_render_edges only on loaded / affected vertices, and replay post-render
    edges of untouched frozen vertices from `artifact_view['edges']`."""
    from checkov.common.graph.graph_builder import CustomAttributes, Edge
    from checkov.terraform.context_parsers.registry import parser_registry
    from checkov.terraform.graph_builder.local_graph import (
        CROSS_VARIABLE_EDGE_PREFIX, S3_BUCKET_REFERENCE_ATTRIBUTE, S3_BUCKET_RESOURCE_NAME, S3ConnectedResources
    )

    eager: list[int] = [i for i, v in enumerate(graph.vertices)
                        if i in affected or getattr(v, "_rendered_loader", None) is None]
    for i in eager:
        vertex = graph.vertices[i]
        for attribute_key, breadcrumbs_list in vertex.changed_attributes.items():
            hash_breadcrumbs = []
            for breadcrumb in breadcrumbs_list:
                v = graph.vertices[breadcrumb.vertex_id]
                bdata = v.get_export_data()
                bdata["module_connection"] = graph._determine_if_module_connection(breadcrumbs_list, v)
                hash_breadcrumbs.append(bdata)
            vertex.breadcrumbs[attribute_key] = hash_breadcrumbs
        if len(vertex.source_module) == 1:
            v = vertex
            source_module_data = []
            while len(v.source_module) == 1:
                idx = list(v.source_module)[0]
                v = graph.vertices[idx]
                module_data = v.get_export_data()
                module_data["idx"] = idx
                if hasattr(vertex, "source_module_object"):
                    module_data["source_module_object"] = v.source_module_object
                source_module_data.append(module_data)
            source_module_data.reverse()
            vertex.breadcrumbs[CustomAttributes.SOURCE_MODULE] = source_module_data
    for i in eager:
        vertex = graph.vertices[i]
        if vertex.attributes.get(CustomAttributes.TF_RESOURCE_ADDRESS) is not None:
            continue
        if vertex.block_type not in parser_registry.context_parsers:
            continue
        source_module = vertex.breadcrumbs.get(CustomAttributes.SOURCE_MODULE)
        address_prefix = ""
        if source_module:
            for module in source_module:
                address_prefix += f"{module.get('type')}.{module.get('name')}."
        context_parser = parser_registry.context_parsers[vertex.block_type]
        entity_context_path = context_parser.get_entity_context_path(vertex.config)
        resource_id = ".".join(entity_context_path) if entity_context_path else vertex.name
        address = f"{address_prefix}{resource_id}"
        vertex.attributes[CustomAttributes.TF_RESOURCE_ADDRESS] = address
        vertex_context = vertex.config
        for path in context_parser.get_entity_definition_path(vertex.config):
            vertex_context = vertex_context.get(path, vertex_context)
        vertex_context[CustomAttributes.TF_RESOURCE_ADDRESS] = address
    affected_providers = {i for i in affected if graph.vertices[i].block_type == BlockType.PROVIDER}
    provider_edge_resources = {
        e.origin for p_i in affected_providers for e in graph.in_edges.get(p_i, ())
        if graph.vertices[e.origin].block_type == BlockType.RESOURCE
    }
    provider_targets = sorted(set(eager) | set(getattr(graph, "_dfo_provider_seeds", ())) | provider_edge_resources)
    if provider_targets and not graph.vertices_by_module_dependency:
        needed_sm_objs: set[Any] = set()
        for i in provider_targets:
            if graph.vertices[i].block_type == BlockType.RESOURCE:
                cur_sm = graph.vertices[i].source_module_object
                needed_sm_objs.add(cur_sm)
                while cur_sm is not None:
                    cur_sm = cur_sm.nested_tf_module
                    needed_sm_objs.add(cur_sm)
        for idx, b in enumerate(graph.vertices):
            if b.block_type == BlockType.PROVIDER and b.source_module_object in needed_sm_objs:
                if getattr(b, "_rendered_loader", None) is None \
                        and b.attributes.get(CustomAttributes.TF_RESOURCE_ADDRESS) is None \
                        and b.block_type in parser_registry.context_parsers:
                    chain_parts_p: list[str] = []
                    cur_mp = b.source_module_object
                    while cur_mp is not None:
                        m_name_p = cur_mp.name
                        if cur_mp.foreach_idx is not None and m_name_p and "[" not in m_name_p:
                            q_p = '"' if isinstance(cur_mp.foreach_idx, str) and not cur_mp.foreach_idx.isnumeric() else ""
                            m_name_p = f"{m_name_p}[{q_p}{cur_mp.foreach_idx}{q_p}]"
                        chain_parts_p.append(f"module.{m_name_p}.")
                        cur_mp = cur_mp.nested_tf_module
                    chain_parts_p.reverse()
                    cp_p = parser_registry.context_parsers[b.block_type]
                    ec_p = cp_p.get_entity_context_path(b.config)
                    addr_p = "".join(chain_parts_p) + (".".join(ec_p) if ec_p else b.name)
                    b.attributes[CustomAttributes.TF_RESOURCE_ADDRESS] = addr_p
                    v_ctx_p = b.config
                    for p_part in cp_p.get_entity_definition_path(b.config):
                        v_ctx_p = v_ctx_p.get(p_part, v_ctx_p)
                    v_ctx_p[CustomAttributes.TF_RESOURCE_ADDRESS] = addr_p
                graph.vertices_by_module_dependency[b.source_module_object][b.block_type].append(idx)
    for i in provider_targets:
        if os.getenv("DFO_NEGATIVE", "") == "provider_pass_aborts":
            v = graph.vertices[i]
            if v.block_type == BlockType.RESOURCE:
                v.attributes.pop(CustomAttributes.PROVIDER_ADDRESS, None)
                v_name = v.name.split(".")
                if len(v_name) >= 2 and isinstance(v.config.get(v_name[0], {}).get(v_name[1]), dict):
                    v.config[v_name[0]][v_name[1]].pop(CustomAttributes.PROVIDER_ADDRESS, None)
            graph._add_provider_attr_to_resource(v)
            continue
        try:
            v = graph.vertices[i]
            if v.block_type == BlockType.RESOURCE:
                if i in affected or i in getattr(graph, "_dfo_provider_seeds", ()) \
                        or i in provider_edge_resources \
                        or not getattr(v, "dfo_reused_unchanged", False):
                    if getattr(v, "_rendered_loader", None) is not None:
                        v._ensure_loaded()
                    if v.attributes.get(CustomAttributes.TF_RESOURCE_ADDRESS) is None:
                        chain_parts: list[str] = []
                        cur_m = v.source_module_object
                        while cur_m is not None:
                            m_name = cur_m.name
                            if cur_m.foreach_idx is not None and m_name and "[" not in m_name:
                                q = '"' if isinstance(cur_m.foreach_idx, str) and not cur_m.foreach_idx.isnumeric() else ""
                                m_name = f"{m_name}[{q}{cur_m.foreach_idx}{q}]"
                            chain_parts.append(f"module.{m_name}.")
                            cur_m = cur_m.nested_tf_module
                        chain_parts.reverse()
                        addr = "".join(chain_parts) + v.name
                        v.attributes[CustomAttributes.TF_RESOURCE_ADDRESS] = addr
                        cp = parser_registry.context_parsers[v.block_type]
                        v_ctx = v.config
                        for p_part in cp.get_entity_definition_path(v.config):
                            v_ctx = v_ctx.get(p_part, v_ctx)
                        v_ctx[CustomAttributes.TF_RESOURCE_ADDRESS] = addr
                    v.attributes.pop(CustomAttributes.PROVIDER_ADDRESS, None)
                    v_name = v.name.split(".")
                    if len(v_name) >= 2 and isinstance(v.config.get(v_name[0], {}).get(v_name[1]), dict):
                        v.config[v_name[0]][v_name[1]].pop(CustomAttributes.PROVIDER_ADDRESS, None)
                    graph._add_provider_attr_to_resource(v)
        except Exception as e:
            logging.info(f"Failed to add provider attributes to {graph.vertices[i].name}, error: {str(e)}")
    resources_types = graph.get_resources_types_in_graph()
    aliases = dict(getattr(graph, "dfo_aliases", None) or {
        v.name: {CustomAttributes.BLOCK_TYPE: v.block_type}
        for i in eager for v in (graph.vertices[i],) if "alias" in v.attributes
    })
    eager_set = set(eager)
    raw_stored_edges = artifact_view["cross_edges"] if "cross_edges" in artifact_view else artifact_view["edges"]
    pre_edges: set[tuple[int, int, str]] = set()
    if "cross_edges" not in artifact_view or raw_stored_edges:
        pre_edges = {(e.origin, e.dest, e.label) for e in graph.edges}
    old_post_edges: set[tuple[int, int, str]] = set()
    post_changed: set[int] = set()
    candidates_cross = {
        o for o, v in enumerate(graph.vertices)
        if v.block_type == BlockType.RESOURCE and (
            o in affected
            or not getattr(v, "dfo_reused_unchanged", False)
            or any(e.dest in affected or not getattr(graph.vertices[e.dest], "dfo_reused_unchanged", False)
                   for e in graph.out_edges.get(o, ()) if graph.vertices[e.dest].block_type != BlockType.RESOURCE)
            or any(m in affected for m in v.source_module)
        )
    }
    recompute_cross = {
        o for o in candidates_cross
        if any(graph.vertices[e.dest].block_type != BlockType.RESOURCE for e in graph.out_edges.get(o, ()))
    }
    recompute_s3 = False
    if S3_BUCKET_RESOURCE_NAME in resources_types:
        recompute_s3 = any(
            e.label == S3_BUCKET_REFERENCE_ATTRIBUTE
            and graph.vertices[e.dest].block_type in (BlockType.VARIABLE, BlockType.LOCALS)
            and (o in affected or e.dest in affected or not getattr(graph.vertices[o], "dfo_reused_unchanged", False))
            for o, edges in graph.out_edges.items()
            if graph.vertices[o].block_type == BlockType.RESOURCE
            for e in edges
        )
        if not recompute_s3:
            map_s3: dict[str, int] = by_key if by_key is not None else getattr(graph, "_dfo_unit_key_to_pr", None)
            if map_s3 is None:
                map_s3 = {}
                graph._dfo_unit_key_to_pr = map_s3
            for e_str in raw_stored_edges:
                if S3_BUCKET_REFERENCE_ATTRIBUTE not in e_str:
                    continue
                ok, dk, lbl = json.loads(e_str)
                if lbl == f"{CROSS_VARIABLE_EDGE_PREFIX}{S3_BUCKET_REFERENCE_ATTRIBUTE}":
                    o_i = map_s3.get(ok)
                    if o_i is None:
                        o_i = _resolve_key_in_graph(ok, graph, root, map_s3)
                    d_i = map_s3.get(dk)
                    if d_i is None:
                        d_i = _resolve_key_in_graph(dk, graph, root, map_s3)
                    if o_i is None or d_i is None:
                        recompute_s3 = True
                        break
        if not recompute_s3:
            removed_blks = getattr(graph, "dfo_removed_keys", None) or []
            if any(json.loads(rk)[2] in (BlockType.VARIABLE, BlockType.LOCALS) for rk in removed_blks):
                recompute_s3 = True
        if not recompute_s3 and not getattr(graph, "dfo_pre_render_edges_unchanged", False) \
                and not getattr(graph, "dfo_replayed_edges_unchanged", False):
            map_s3_pre: dict[str, int] = by_key if by_key is not None else getattr(graph, "_dfo_unit_key_to_pr", None)
            if map_s3_pre is None:
                map_s3_pre = {}
                graph._dfo_unit_key_to_pr = map_s3_pre
            for e_str in artifact_view["edges"]:
                if S3_BUCKET_REFERENCE_ATTRIBUTE in e_str:
                    ok, dk, lbl = json.loads(e_str)
                    if lbl == S3_BUCKET_REFERENCE_ATTRIBUTE:
                        if json.loads(dk)[2] in (BlockType.VARIABLE, BlockType.LOCALS):
                            o_i = map_s3_pre.get(ok)
                            if o_i is None:
                                o_i = _resolve_key_in_graph(ok, graph, root, map_s3_pre)
                            d_i = map_s3_pre.get(dk)
                            if d_i is None:
                                d_i = _resolve_key_in_graph(dk, graph, root, map_s3_pre)
                            if o_i is None or d_i is None:
                                recompute_s3 = True
                                break
    s3_buckets_with_var_ref = {
        o for o, edges in graph.out_edges.items()
        if graph.vertices[o].block_type == BlockType.RESOURCE
        and graph.vertices[o].name.startswith(f"{S3_BUCKET_RESOURCE_NAME}.")
        and any(e.label == S3_BUCKET_REFERENCE_ATTRIBUTE and graph.vertices[e.dest].block_type in (BlockType.VARIABLE, BlockType.LOCALS) for e in edges)
    } if recompute_s3 else set()
    old_recomputed_post: set[tuple[int, int, str]] = set()
    post_changed: set[int] = set()
    parsed_cross: list[tuple[Optional[int], Optional[int], str]] = []
    for e_str in raw_stored_edges:
        if CROSS_VARIABLE_EDGE_PREFIX not in e_str:
            continue
        origin_key, dest_key, label = json.loads(e_str)
        if not label.startswith(CROSS_VARIABLE_EDGE_PREFIX):
            continue
        map_cross: dict[str, int] = by_key if by_key is not None else getattr(graph, "_dfo_unit_key_to_pr", None)
        if map_cross is None:
            map_cross = {}
            graph._dfo_unit_key_to_pr = map_cross
        o = map_cross.get(origin_key)
        if o is None:
            o = _resolve_key_in_graph(origin_key, graph, root, map_cross)
        d = map_cross.get(dest_key)
        if d is None:
            d = _resolve_key_in_graph(dest_key, graph, root, map_cross)
        parsed_cross.append((o, d, label))
        if (o is None or d is None or d in affected or not getattr(graph.vertices[d], "dfo_reused_unchanged", False)) \
                and o is not None and o not in recompute_cross:
            if graph.vertices[o].block_type == BlockType.RESOURCE and any(
                graph.vertices[e.dest].block_type != BlockType.RESOURCE for e in graph.out_edges.get(o, ())
            ):
                recompute_cross.add(o)
    del raw_stored_edges
    for o, d, label in parsed_cross:
        if o is None or d is None:
            if o is not None:
                post_changed.add(o)
            if d is not None:
                post_changed.add(d)
            continue
        if (o, d, label) in pre_edges:
            continue
        if o not in recompute_cross and getattr(graph.vertices[o], "dfo_reused_unchanged", False) and not (
            recompute_s3 and label == f"{CROSS_VARIABLE_EDGE_PREFIX}{S3_BUCKET_REFERENCE_ATTRIBUTE}"
            and o in s3_buckets_with_var_ref
        ):
            if graph.vertices[o].block_type == BlockType.RESOURCE \
                    and graph.vertices[d].block_type == BlockType.RESOURCE:
                edge = Edge(o, d, label)
                graph.edges.append(edge)
                graph.out_edges[o].append(edge)
                graph.in_edges[d].append(edge)
                pre_edges.add((o, d, label))
                if (o in affected or d in affected or not getattr(graph.vertices[o], "dfo_reused_unchanged", False)
                        or not getattr(graph.vertices[d], "dfo_reused_unchanged", False)):
                    post_changed.add(o)
                    post_changed.add(d)
                    for endpoint in (o, d):
                        ev = graph.vertices[endpoint]
                        if getattr(ev, "_rendered_loader", None) is not None:
                            ev._ensure_loaded()
        else:
            old_recomputed_post.add((o, d, label))
    del parsed_cross
    release_part = getattr(artifact_view, "release_part", None)
    if release_part is not None:
        release_part("edges")
    before_post = len(graph.edges)
    if recompute_cross:
        target_modules: set[Any] = set()
        for o in recompute_cross:
            vertex = graph.vertices[o]
            target_modules.add(vertex.source_module_object)
            v = vertex
            while len(v.source_module) == 1:
                idx = list(v.source_module)[0]
                v = graph.vertices[idx]
                target_modules.add(v.source_module_object)
        if not graph.vertices_by_module_dependency_by_name:
            output_source_modules: set[Any] = set()
            for idx, b in enumerate(graph.vertices):
                if b.block_type == BlockType.OUTPUT:
                    graph.vertices_block_name_map[b.block_type][b.name].append(idx)
                    output_source_modules.add(b.source_module_object)
            for m_obj in output_source_modules:
                if m_obj is not None and m_obj.nested_tf_module in target_modules:
                    target_modules.add(m_obj)
            for idx, b in enumerate(graph.vertices):
                if b.source_module_object in target_modules:
                    graph.vertices_by_module_dependency_by_name[b.source_module_object][b.block_type][b.name].append(idx)
                    if b.block_type != BlockType.PROVIDER:
                        graph.vertices_by_module_dependency[b.source_module_object][b.block_type].append(idx)
        else:
            for idx, b in enumerate(graph.vertices):
                if b.block_type == BlockType.OUTPUT and b.source_module_object is not None \
                        and b.source_module_object.nested_tf_module in target_modules:
                    target_modules.add(b.source_module_object)
        for idx, b in enumerate(graph.vertices):
            if b.block_type == BlockType.MODULE and b.source_module_object in target_modules:
                if getattr(b, "_rendered_loader", None) is not None and idx in affected:
                    b._ensure_loaded()
        for sm_obj in target_modules:
            bmap = graph.vertices_by_module_dependency_by_name.get(sm_obj, {})
            for btype in (BlockType.RESOURCE, BlockType.DATA):
                name_map = bmap.get(btype, {})
                indexed_bases = {k_name.split("[", 1)[0] for k_name in name_map if "[" in k_name}
                for k_name, j_list in name_map.items():
                    if len(j_list) > 1 or "[" in k_name or k_name in indexed_bases:
                        for j in j_list:
                            b = graph.vertices[j]
                            if getattr(b, "_rendered_loader", None) is not None \
                                    and (b.for_each_index is not None or "[" in b.name):
                                b._ensure_loaded()
                            if getattr(b, "_rendered_loader", None) is None:
                                if b.attributes.get(CustomAttributes.TF_RESOURCE_ADDRESS) is None:
                                    chain_parts: list[str] = []
                                    cur_m = b.source_module_object
                                    while cur_m is not None:
                                        m_name = cur_m.name
                                        if cur_m.foreach_idx is not None and m_name and "[" not in m_name:
                                            q = '"' if isinstance(cur_m.foreach_idx, str) and not cur_m.foreach_idx.isnumeric() else ""
                                            m_name = f"{m_name}[{q}{cur_m.foreach_idx}{q}]"
                                        chain_parts.append(f"module.{m_name}.")
                                        cur_m = cur_m.nested_tf_module
                                    chain_parts.reverse()
                                    cp_b = parser_registry.context_parsers.get(b.block_type)
                                    ec_b = cp_b.get_entity_context_path(b.config) if cp_b else None
                                    res_b = ".".join(ec_b) if ec_b else b.name
                                    b.attributes[CustomAttributes.TF_RESOURCE_ADDRESS] = "".join(chain_parts) + res_b
    for o in sorted(recompute_cross):
        vertex = graph.vertices[o]
        if any(graph.vertices[e.dest].block_type != BlockType.RESOURCE for e in graph.out_edges.get(o, ())):
            if getattr(vertex, "_rendered_loader", None) is not None:
                vertex._ensure_loaded()
            if len(vertex.source_module) == 1 and CustomAttributes.SOURCE_MODULE not in vertex.breadcrumbs:
                v = vertex
                sdata = []
                while len(v.source_module) == 1:
                    idx = list(v.source_module)[0]
                    v = graph.vertices[idx]
                    mdata = v.get_export_data()
                    mdata["idx"] = idx
                    if hasattr(vertex, "source_module_object"):
                        mdata["source_module_object"] = v.source_module_object
                    sdata.append(mdata)
                sdata.reverse()
                vertex.breadcrumbs[CustomAttributes.SOURCE_MODULE] = sdata
            modules = vertex.breadcrumbs.get(CustomAttributes.SOURCE_MODULE, [])
            b4_cross = len(graph.edges)
            graph._build_edges_for_vertex(o, vertex, aliases, resources_types, True, modules)
            for ce in graph.edges[b4_cross:]:
                dv = graph.vertices[ce.dest]
                if getattr(dv, "_rendered_loader", None) is not None:
                    dv._ensure_loaded()
                if ce.origin in affected or ce.dest in affected \
                        or not getattr(graph.vertices[ce.origin], "dfo_reused_unchanged", False) \
                        or not getattr(dv, "dfo_reused_unchanged", False):
                    post_changed.add(ce.origin)
                    post_changed.add(ce.dest)
    if recompute_s3:
        s3_buckets_mapping: dict[int, S3ConnectedResources] = {}
        for origin_node_index, referenced_vertices in graph.out_edges.items():
            vertex = graph.vertices[origin_node_index]
            if vertex.block_type != BlockType.RESOURCE:
                continue
            for referenced_vertice in referenced_vertices:
                if referenced_vertice.label == S3_BUCKET_REFERENCE_ATTRIBUTE:
                    current = s3_buckets_mapping.get(referenced_vertice.dest,
                                                     {"bucket_resource_index": None, "referenced_vertices": []})
                    if vertex.name.startswith(f"{S3_BUCKET_RESOURCE_NAME}."):
                        current["bucket_resource_index"] = origin_node_index
                    else:
                        current["referenced_vertices"].append(referenced_vertice)
                    s3_buckets_mapping[referenced_vertice.dest] = current
        for destination, mapping in s3_buckets_mapping.items():
            if graph.vertices[destination].block_type in [BlockType.VARIABLE, BlockType.LOCALS]:
                if mapping["bucket_resource_index"] is None:
                    continue
                b_idx = mapping["bucket_resource_index"]
                for reference_vertex in mapping["referenced_vertices"]:
                    r_orig = reference_vertex.origin
                    graph.create_edge(b_idx, r_orig, S3_BUCKET_REFERENCE_ATTRIBUTE, True)
                    if b_idx in affected or r_orig in affected or destination in affected \
                            or not getattr(graph.vertices[b_idx], "dfo_reused_unchanged", False) \
                            or not getattr(graph.vertices[r_orig], "dfo_reused_unchanged", False):
                        post_changed.add(b_idx)
                        post_changed.add(r_orig)
    new_recomputed_post = {(e.origin, e.dest, e.label) for e in graph.edges[before_post:]} | (pre_edges & old_recomputed_post)
    for o, d, _ in old_recomputed_post ^ new_recomputed_post:
        post_changed.add(o)
        post_changed.add(d)
    for idx in post_changed:
        if 0 <= idx < len(graph.vertices):
            pv = graph.vertices[idx]
            if getattr(pv, "_rendered_loader", None) is not None:
                pv._ensure_loaded()
    return post_changed


def unconverged_vertices(renderer: Any, graph: Any, root: str) -> set[str]:
    """Vertices with outgoing edges the render loop never completed (it stopped at its cap)."""
    keys = vertex_keys(graph, root)
    pending = set()
    for origin, edges in graph.out_edges.items():
        done = set(renderer.done_edges_by_origin_vertex.get(origin, []))
        if edges and not set(edges).issubset(done):
            pending.add(keys[origin])
    return pending
