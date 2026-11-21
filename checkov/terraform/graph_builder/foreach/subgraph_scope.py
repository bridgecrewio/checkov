"""Scoped count / for_each sub-graph render (opt-in: CHECKOV_FOREACH_SUBGRAPH_SCOPE=true, set by the diff scan).

The count / for_each handlers render a copy of the graph (`_build_sub_graph` + `_render_sub_graph`) only to read the
rendered `count` / `for_each` attributes of blocks afterwards; the copy is then discarded. An edge evaluation writes
only its origin vertex and reads only its origin and destination. So the attributes of a set S of vertices depend
only on evaluations whose origin is in closure(S) = S plus every vertex reachable from S through out-edges, and every
other evaluation can be skipped without changing any value in closure(S).

S = the blocks to render plus every vertex carrying a `count` or `for_each` attribute (the handlers read exactly
these; rendering never adds a `count` / `for_each` key to a vertex that has none: an edge's label is an existing
attribute of its origin). Skipping uses the renderer's frozen-vertex filter inside the global loop, whose schedule
does not depend on evaluation results (affected_schedule.py), so the remaining evaluations run in the same order.
The dynamic-block pass after the loop skips the same vertices; it writes only the vertex it processes.

Test mode CHECKOV_FOREACH_SUBGRAPH_SCOPE_VERIFY=true also renders an untouched copy the original way and fails if any
vertex of closure(S) differs.
"""
from __future__ import annotations

import json
import os
from typing import TYPE_CHECKING, Any

from checkov.common.graph.graph_builder.deterministic import incremental_graph_enabled
from checkov.common.util.data_structures_utils import pickle_deepcopy
from checkov.terraform.graph_builder.foreach.consts import COUNT_STRING, FOREACH_STRING

if TYPE_CHECKING:
    from checkov.terraform.graph_builder.local_graph import TerraformLocalGraph

SCOPE_ENV = "CHECKOV_FOREACH_SUBGRAPH_SCOPE"
VERIFY_ENV = "CHECKOV_FOREACH_SUBGRAPH_SCOPE_VERIFY"


def subgraph_scope_enabled() -> bool:
    """Also requires incremental mode: upstream appends the origin's breadcrumbs to the DESTINATION's list (a write
    outside the origin vertex); incremental mode copies the list instead (LocalGraph.update_vertex_attribute)."""
    return incremental_graph_enabled() and os.getenv(SCOPE_ENV, "false").lower() == "true"


def subgraph_scope_verification_enabled() -> bool:
    return os.getenv(VERIFY_ENV, "false").lower() == "true"


def read_closure(sub_graph: TerraformLocalGraph, blocks_to_render: list[int]) -> set[int]:
    seeds = {i for i in blocks_to_render if 0 <= i < len(sub_graph.vertices)}
    seeds |= {i for i, vertex in enumerate(sub_graph.vertices)
              if vertex and (FOREACH_STRING in vertex.attributes or COUNT_STRING in vertex.attributes)}
    closure = set(seeds)
    stack = list(seeds)
    while stack:
        for edge in sub_graph.out_edges.get(stack.pop(), []):
            if edge.dest not in closure:
                closure.add(edge.dest)
                stack.append(edge.dest)
    return closure


def unread_vertices(sub_graph: TerraformLocalGraph, blocks_to_render: list[int]) -> set[int]:
    return set(range(len(sub_graph.vertices))) - read_closure(sub_graph, blocks_to_render)


def placeholder_vertices(sub_graph: TerraformLocalGraph) -> set[int]:
    """Resources the sub-graph leaves out are `{}` placeholders; every evaluation touching one returns immediately
    (TerraformVariableRenderer.evaluate_vertex_attribute_from_edge), so skipping their groups changes nothing."""
    return {i for i, vertex in enumerate(sub_graph.vertices) if not vertex}


def copy_for_reference(sub_graph: TerraformLocalGraph) -> TerraformLocalGraph:
    from checkov.terraform.graph_builder.local_graph import TerraformLocalGraph

    reference = TerraformLocalGraph(sub_graph.module)
    reference.vertices = pickle_deepcopy(sub_graph.vertices)
    reference.edges = sub_graph.edges
    reference.in_edges = sub_graph.in_edges
    reference.out_edges = sub_graph.out_edges
    return reference


PRECISE_ENV = "CHECKOV_FOREACH_SUBGRAPH_PRECISE"
"""Opt-in (on top of SCOPE_ENV): attribute-precise read set instead of the vertex closure (see `precise_read_set`)."""

STATEMENT_ATTRIBUTES = (COUNT_STRING, FOREACH_STRING)
NEGATIVE_CONTROL = os.getenv("DFO_NEGATIVE", "")
"""PoC test hook: `precise_scope_skip_destinations` follows no edge out of a narrowed vertex (a count's variables are
never rendered); the verifier and the correctness suite must observe it."""


def subgraph_precise_enabled() -> bool:
    return subgraph_scope_enabled() and os.getenv(PRECISE_ENV, "false").lower() == "true"


class PreciseScopeUnsafe(Exception):
    """A narrowed read assumption does not hold at evaluation time: the caller re-renders with the vertex closure."""


def _seeds(sub_graph: TerraformLocalGraph, blocks_to_render: list[int]) -> set[int]:
    seeds = {i for i in blocks_to_render if 0 <= i < len(sub_graph.vertices) and sub_graph.vertices[i]}
    seeds |= {i for i, vertex in enumerate(sub_graph.vertices)
              if vertex and (FOREACH_STRING in vertex.attributes or COUNT_STRING in vertex.attributes)}
    return seeds


def _label_in(label: str, attrs: set[str]) -> bool:
    if label in attrs:
        return True
    return any(label.startswith(a + ".") or a.startswith(label + ".") for a in attrs)


def _merge(wanted: dict[int, set[str] | None], index: int, attrs: set[str] | None) -> bool:
    if index not in wanted:
        wanted[index] = None if attrs is None else set(attrs)
        return True
    current = wanted[index]
    if current is None:
        return False
    if attrs is None:
        wanted[index] = None
        return True
    if attrs <= current:
        return False
    current |= attrs
    return True


def is_narrowed_module_input(origin: Any, dest: Any) -> bool:
    """variable -> module edge (the module-call input edge): evaluating it reads only `dest.attributes[origin.name]`
    as long as the variable's value holds no module-typed reference (TerraformVariableRenderer.
    evaluate_vertex_attribute_from_edge: without references it copies that one attribute; with references,
    find_path_from_referenced_vertices matches a module destination only for module-typed references).
    Static part: the module's input expression itself references no module (it is what the variable receives);
    the dynamic part is checked at evaluation time (`guard_module_inputs`)."""
    from checkov.terraform.graph_builder.graph_components.block_types import BlockType

    if origin.block_type != BlockType.VARIABLE or dest.block_type != BlockType.MODULE:
        return False
    return not _holds_module_reference(dest.attributes.get(origin.name))


def _holds_module_reference(value: Any) -> bool:
    """Conservative: every module-typed reference contains the text `module.` (a false positive only costs the
    precise scope)."""
    if value is None or isinstance(value, (bool, int, float)):
        return False
    return "module." in (value if isinstance(value, str) else str(value))


def precise_read_set(sub_graph: TerraformLocalGraph, blocks_to_render: list[int]) -> dict[int, set[str] | None]:
    """vertex -> attribute names whose rendered value the handlers can observe (None = every attribute).

    The handlers read only `count` / `for_each` of the seeds. An edge group (origin, label) writes only
    origin.attributes[label] (and its dotted prefixes / suffixes, matched by `_label_in`), from that value and the
    destination. The destination is read as a whole, except a module reached through a module-call input edge
    (`is_narrowed_module_input`, guarded at evaluation time). Placeholder resources (`{}`) are never read."""
    wanted: dict[int, set[str] | None] = {}
    for seed in _seeds(sub_graph, blocks_to_render):
        attributes = sub_graph.vertices[seed].attributes
        _merge(wanted, seed, {a for a in STATEMENT_ATTRIBUTES if a in attributes})
    stack = list(wanted)
    while stack:
        index = stack.pop()
        attrs = wanted[index]
        origin = sub_graph.vertices[index]
        for edge in sub_graph.out_edges.get(index, []):
            dest = sub_graph.vertices[edge.dest]
            if not dest or (attrs is not None and not _label_in(edge.label, attrs)):
                continue
            if NEGATIVE_CONTROL == "precise_scope_skip_destinations" and attrs is not None:
                continue
            dest_attrs = {origin.name} if is_narrowed_module_input(origin, dest) else None
            if _merge(wanted, edge.dest, dest_attrs):
                stack.append(edge.dest)
    return wanted


def label_filter(wanted: dict[int, set[str] | None]) -> Any:
    def evaluated(origin: int, label: str) -> bool:
        attrs = wanted.get(origin)
        return attrs is None or _label_in(label, attrs)
    return evaluated


def guard_module_inputs(renderer: Any, wanted: dict[int, set[str] | None]) -> None:
    """Wraps the renderer's edge evaluation: a narrowed module-input edge whose variable value now holds a
    module-typed reference would read other module attributes -> PreciseScopeUnsafe."""
    from checkov.terraform.graph_builder.graph_components.block_types import BlockType

    graph = renderer.local_graph
    evaluate = renderer.evaluate_vertex_attribute_from_edge

    def guarded(edge_list: list[Any]) -> None:
        for edge in edge_list:
            dest = graph.vertices[edge.dest]
            origin = graph.vertices[edge.origin]
            if not dest or not origin or wanted.get(edge.dest) is None \
                    or origin.block_type != BlockType.VARIABLE or dest.block_type != BlockType.MODULE:
                continue
            if _holds_module_reference(origin.attributes.get(edge.label, "")) \
                    or _holds_module_reference(dest.attributes.get(origin.name)):
                raise PreciseScopeUnsafe(f"module reference in {origin.name}.{edge.label}")
        evaluate(edge_list)

    renderer.evaluate_vertex_attribute_from_edge = guarded


def statement_state(sub_graph: TerraformLocalGraph, index: int) -> str:
    vertex = sub_graph.vertices[index]
    if not vertex:
        return ""
    return json.dumps({a: vertex.attributes.get(a) for a in STATEMENT_ATTRIBUTES}, sort_keys=True, default=str)


def assert_same_statements(scoped: TerraformLocalGraph, reference: TerraformLocalGraph,
                           blocks_to_render: list[int]) -> None:
    seeds = _seeds(reference, blocks_to_render)
    differing = [i for i in sorted(seeds) if statement_state(scoped, i) != statement_state(reference, i)]
    if differing:
        raise RuntimeError(f"precise count/for_each sub-graph render differs from the full sub-graph render on "
                           f"{len(differing)} statements, e.g. {differing[:5]}")


def _state(vertex: Any) -> str:
    return json.dumps(vertex.attributes, sort_keys=True, default=str) if vertex else ""


def assert_same_closure(scoped: TerraformLocalGraph, reference: TerraformLocalGraph, closure: set[int]) -> None:
    differing = [i for i in sorted(closure) if _state(scoped.vertices[i]) != _state(reference.vertices[i])]
    if differing:
        raise RuntimeError(f"scoped count/for_each sub-graph render differs from the full sub-graph render on "
                           f"{len(differing)} vertices, e.g. {differing[:5]}")
