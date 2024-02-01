from __future__ import annotations

from typing import Any

from networkx import DiGraph
from rustworkx import PyDiGraph

from checkov.common.graph.db_connectors.networkx.networkx_db_connector import NetworkxConnector
from checkov.common.graph.db_connectors.rustworkx.rustworkx_db_connector import RustworkxConnector
from checkov.common.typing import LibraryGraph

GRAPH_FRAMEWORKS = ['NETWORKX', 'RUSTWORKX']
PARAMETERIZED_GRAPH_FRAMEWORKS = [
    {"graph_framework": "NETWORKX"},
    {"graph_framework": "RUSTWORKX"}
]


def set_db_connector_by_graph_framework(graph_framework: str) -> Any:
    if graph_framework == 'NETWORKX':
        return NetworkxConnector()
    elif graph_framework == 'RUSTWORKX':
        return RustworkxConnector()
    return None


def set_graph_by_graph_framework(graph_framework: str) -> LibraryGraph:
    if graph_framework == 'NETWORKX':
        graph = DiGraph()
    else:  # graph_framework == 'RUSTWORKX'
        graph = PyDiGraph()
    return graph


def set_graph_with_resource_by_graph_framework(graph_framework: str, resource: dict[str, Any], module_resource: dict[str, Any] | None = None) -> LibraryGraph:
    if graph_framework == 'NETWORKX':
        graph = DiGraph()
        graph.add_node(1, **resource)
        if module_resource:
            graph.add_node(2, **module_resource)

    else:  # graph_framework == 'RUSTWORKX'
        graph = PyDiGraph()
        graph.add_node((0, resource))
        if module_resource:
            graph.add_node((1, module_resource))

    return graph


def add_vertices_to_graph_by_graph_framework(graph_framework: str, vertices: dict[str, Any], graph: LibraryGraph, index: int = 1, name: str = '1', block_type: str = 'resource') -> None:
    if graph_framework == 'NETWORKX':
        graph.add_node(index, **vertices)

    else:  # graph_framework == 'RUSTWORKX'
        graph.add_node((index-1, vertices))
