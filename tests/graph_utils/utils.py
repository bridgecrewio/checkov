from __future__ import annotations

from typing import Any

import igraph
from networkx import DiGraph
from rustworkx import PyDiGraph

from checkov.common.graph.db_connectors.igraph.igraph_db_connector import IgraphConnector
from checkov.common.graph.db_connectors.networkx.networkx_db_connector import NetworkxConnector
from checkov.common.graph.db_connectors.rustworkx.rustworkx_db_connector import RustworkxConnector
from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.typing import LibraryGraph

GRAPH_FRAMEWORKS = ['NETWORKX', 'IGRAPH', 'RUSTWORKX']
PARAMETERIZED_GRAPH_FRAMEWORKS = [
    {"graph_framework": "NETWORKX"},
    {"graph_framework": "IGRAPH"},
    {"graph_framework": "RUSTWORKX"}
]


def set_db_connector_by_graph_framework(graph_framework: str) -> Any:
    if graph_framework == 'NETWORKX':
        return NetworkxConnector()
    elif graph_framework == 'IGRAPH':
        return IgraphConnector()
    elif graph_framework == 'RUSTWORKX':
        return RustworkxConnector()
    return None


def set_graph_by_graph_framework(graph_framework: str) -> LibraryGraph:
    if graph_framework == 'NETWORKX':
        graph = DiGraph()
    elif graph_framework == 'IGRAPH':
        graph = igraph.Graph()
    else:  # graph_framework == 'RUSTWORKX'
        graph = PyDiGraph()
    return graph


def set_graph_with_resource_by_graph_framework(graph_framework: str, resource: dict[str, Any], module_resource: dict[str, Any] | None = None) -> LibraryGraph:
    if graph_framework == 'IGRAPH':
        graph = igraph.Graph()
        attr = resource
        graph.add_vertex(
            name='1',
            block_type_='resource',
            resource_type=attr[CustomAttributes.RESOURCE_TYPE] if CustomAttributes.RESOURCE_TYPE in attr else None,
            attr=attr,
        )
        if module_resource:
            graph.add_vertex(
                name='batch',
                block_type_='module',
                resource_type=module_resource[
                    CustomAttributes.RESOURCE_TYPE] if CustomAttributes.RESOURCE_TYPE in module_resource else None,
                attr=module_resource,
            )

    elif graph_framework == 'NETWORKX':
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
    if graph_framework == 'IGRAPH':
        graph.add_vertex(
            name=name,
            block_type_=block_type,
            resource_type=vertices[CustomAttributes.RESOURCE_TYPE] if CustomAttributes.RESOURCE_TYPE in vertices else None,
            attr=vertices,
        )
    elif graph_framework == 'NETWORKX':
        graph.add_node(index, **vertices)

    else:  # graph_framework == 'RUSTWORKX'
        graph.add_node((index-1, vertices))
