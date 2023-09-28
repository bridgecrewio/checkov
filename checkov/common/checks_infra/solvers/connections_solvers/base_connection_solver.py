from __future__ import annotations

import itertools
from typing import Any, List, Dict, Optional, Tuple, TYPE_CHECKING

from igraph import Graph
from networkx import DiGraph

from checkov.common.graph.checks_infra.enums import SolverType
from checkov.common.graph.checks_infra.solvers.base_solver import BaseSolver
from checkov.common.graph.graph_builder import CustomAttributes
from checkov.terraform.graph_builder.graph_components.block_types import BlockType

if TYPE_CHECKING:
    from checkov.common.typing import LibraryGraph


class BaseConnectionSolver(BaseSolver):
    # resource is automatically supported
    SUPPORTED_CONNECTION_BLOCK_TYPES = (BlockType.OUTPUT,)

    def __init__(
        self,
        resource_types: List[str],
        connected_resources_types: List[str],
        vertices_under_resource_types: Optional[List[Dict[str, Any]]] = None,
        vertices_under_connected_resources_types: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        super().__init__(SolverType.CONNECTION)
        self.resource_types = resource_types
        self.connected_resources_types = connected_resources_types
        self.targeted_resources_types = set(itertools.chain(resource_types, connected_resources_types))
        self.vertices_under_resource_types = vertices_under_resource_types or []
        self.vertices_under_connected_resources_types = vertices_under_connected_resources_types or []
        self.excluded_vertices: List[Dict[str, Any]] = []
        self.unknown_vertices: List[Dict[str, Any]] = []

    def run(self, graph_connector: LibraryGraph) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
        self.set_vertices(graph_connector, [], [])

        subgraph = self.reduce_graph_by_target_types(graph_connector)

        return self.get_operation(subgraph)

    def is_associated_edge(self, origin_type: str, destination_type: str) -> bool:
        return (origin_type in self.resource_types and destination_type in self.connected_resources_types) or (
            origin_type in self.connected_resources_types and destination_type in self.resource_types
        )

    def is_associated_vertex(self, vertex_type: str) -> bool:
        return vertex_type in itertools.chain(self.resource_types, self.connected_resources_types)

    def set_vertices(self, graph_connector: LibraryGraph, exclude_vertices: List[Dict[str, Any]], unknown_vertices: List[Dict[str, Any]]) -> None:
        if isinstance(graph_connector, Graph):
            select_kwargs = {}
            if self.resource_types:
                select_kwargs = {"resource_type_in": self.resource_types}

            self.vertices_under_resource_types = [
                data for data in graph_connector.vs.select(**select_kwargs)["attr"]
            ]
            self.vertices_under_connected_resources_types = [
                data for data in graph_connector.vs.select(resource_type_in=self.connected_resources_types)["attr"]
            ]
        elif isinstance(graph_connector, DiGraph):
            self.vertices_under_resource_types = [
                v for _, v in graph_connector.nodes(data=True) if self.resource_type_pred(v, self.resource_types)
            ]
            self.vertices_under_connected_resources_types = [
                v for _, v in graph_connector.nodes(data=True) if self.resource_type_pred(v, self.connected_resources_types)
            ]

        # isinstance(graph_connector, PyDiGraph):
        else:
            self.vertices_under_resource_types = [
                v for _, v in graph_connector.nodes() if self.resource_type_pred(v, self.resource_types)
            ]
            self.vertices_under_connected_resources_types = [
                v for _, v in graph_connector.nodes() if
                self.resource_type_pred(v, self.connected_resources_types)
            ]

        self.excluded_vertices = [
            v
            for v in itertools.chain(self.vertices_under_resource_types, self.vertices_under_connected_resources_types)
            if v in exclude_vertices
        ]
        self.unknown_vertices = [
            v
            for v in itertools.chain(self.vertices_under_resource_types, self.vertices_under_connected_resources_types)
            if v in unknown_vertices
        ]

    def reduce_graph_by_target_types(self, graph_connector: LibraryGraph) -> LibraryGraph:
        # no need to create a subgraph, if there are no vertices to be checked
        if not self.vertices_under_resource_types:
            return graph_connector

        if isinstance(graph_connector, Graph):
            resource_nodes = {
                vertex for vertex in graph_connector.vs.select(resource_type_in=self.targeted_resources_types)
            }
            connection_nodes = {
                vertex for vertex in graph_connector.vs.select(block_type__in=BaseConnectionSolver.SUPPORTED_CONNECTION_BLOCK_TYPES)
            }
        elif isinstance(graph_connector, DiGraph):
            resource_nodes = {
                node
                for node, resource_type in graph_connector.nodes(data=CustomAttributes.RESOURCE_TYPE)
                if resource_type in self.targeted_resources_types
            }

            # tuple needs to be adjusted, if more connection block types are supported
            connection_nodes = {
                node
                for node, block_type in graph_connector.nodes(data=CustomAttributes.BLOCK_TYPE)
                if block_type in BaseConnectionSolver.SUPPORTED_CONNECTION_BLOCK_TYPES
            }

        # isinstance(graph_connector, PyDiGraph):
        else:
            resource_nodes = {
                index
                for index, node in graph_connector.nodes()
                if self.resource_type_pred(node, list(self.targeted_resources_types))
            }

            # tuple needs to be adjusted, if more connection block types are supported
            connection_nodes = {
                index
                for index, node in graph_connector.nodes()
                if node['block_type_'] in BaseConnectionSolver.SUPPORTED_CONNECTION_BLOCK_TYPES
            }

        resource_nodes.update(connection_nodes)

        return graph_connector.subgraph(list(resource_nodes))

    def populate_checks_results(self, origin_attributes: Dict[str, Any], destination_attributes: Dict[str, Any], passed: List[Dict[str, Any]], failed: List[Dict[str, Any]], unknown: List[Dict[str, Any]]) -> None:
        if origin_attributes in self.excluded_vertices or destination_attributes in self.excluded_vertices:
            failed.extend([origin_attributes, destination_attributes])
        elif origin_attributes in self.unknown_vertices or destination_attributes in self.unknown_vertices:
            unknown.extend([origin_attributes, destination_attributes])
        else:
            passed.extend([origin_attributes, destination_attributes])

    def get_operation(self, graph_connector: LibraryGraph) -> \
            Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
        raise NotImplementedError

    def _get_operation(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError
