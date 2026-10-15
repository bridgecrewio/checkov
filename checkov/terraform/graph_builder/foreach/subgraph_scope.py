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


def _state(vertex: Any) -> str:
    return json.dumps(vertex.attributes, sort_keys=True, default=str) if vertex else ""


def assert_same_closure(scoped: TerraformLocalGraph, reference: TerraformLocalGraph, closure: set[int]) -> None:
    differing = [i for i in sorted(closure) if _state(scoped.vertices[i]) != _state(reference.vertices[i])]
    if differing:
        raise RuntimeError(f"scoped count/for_each sub-graph render differs from the full sub-graph render on "
                           f"{len(differing)} vertices, e.g. {differing[:5]}")
