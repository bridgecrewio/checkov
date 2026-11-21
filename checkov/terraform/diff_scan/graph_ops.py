"""Index-level operations on a pre-render TerraformLocalGraph."""
from __future__ import annotations

from typing import Any

from checkov.common.graph.graph_builder import Edge
from checkov.terraform.graph_builder.local_graph import TerraformLocalGraph


def set_edges(graph: TerraformLocalGraph, edges: list[tuple[int, int, str]]) -> None:
    """Replace the graph's edge list (and in/out maps) with `edges`, in the given order."""
    graph.edges = []
    for index in range(len(graph.vertices)):
        graph.in_edges[index] = []
        graph.out_edges[index] = []
    for origin, dest, label in edges:
        edge = Edge(origin, dest, label)
        graph.edges.append(edge)
        graph.out_edges[origin].append(edge)
        graph.in_edges[dest].append(edge)


def permute(graph: TerraformLocalGraph, order: list[int]) -> None:
    """Reorder vertices: new position p holds old vertex order[p]. Every index-valued field follows."""
    new_position = {old: new for new, old in enumerate(order)}
    edges = [(new_position[e.origin], new_position[e.dest], e.label) for e in graph.edges]
    graph.vertices = [graph.vertices[old] for old in order]
    for vertex in graph.vertices:
        vertex.source_module = {new_position[i] for i in vertex.source_module}
        vertex.module_connections = {attr: [new_position[i] for i in ids]
                                     for attr, ids in vertex.module_connections.items()}
    graph._arrange_graph_data()
    set_edges(graph, edges)


def edge_tuples(graph: TerraformLocalGraph) -> list[tuple[int, int, str]]:
    return [(e.origin, e.dest, e.label) for e in graph.edges]


def index_fields(vertex: Any) -> tuple[set[int], dict[str, list[int]]]:
    return set(vertex.source_module), {k: list(v) for k, v in vertex.module_connections.items()}
