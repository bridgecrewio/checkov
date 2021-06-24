import itertools
from typing import Any, List, Dict, Optional, Tuple

from networkx import DiGraph

from checkov.common.graph.checks_infra.enums import SolverType
from checkov.common.graph.checks_infra.solvers.base_solver import BaseSolver


class BaseConnectionSolver(BaseSolver):
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
        self.vertices_under_resource_types = vertices_under_resource_types or []
        self.vertices_under_connected_resources_types = vertices_under_connected_resources_types or []
        self.excluded_vertices: List[Dict[str, Any]] = []

    def run(self, graph_connector: DiGraph) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        self.set_vertices(graph_connector, [])
        return self.get_operation(graph_connector)

    def is_associated_edge(self, origin_type: str, destination_type: str) -> bool:
        return (origin_type in self.resource_types and destination_type in self.connected_resources_types) or (
            origin_type in self.connected_resources_types and destination_type in self.resource_types
        )

    def is_associated_vertex(self, vertex_type: str) -> bool:
        return vertex_type in itertools.chain(self.resource_types, self.connected_resources_types)

    def set_vertices(self, graph_connector: DiGraph, exclude_vertices: List[Dict[str, Any]]) -> None:
        self.vertices_under_resource_types = [
            v for _, v in graph_connector.nodes(data=True) if self.resource_type_pred(v, self.resource_types)
        ]
        self.vertices_under_connected_resources_types = [
            v for _, v in graph_connector.nodes(data=True) if self.resource_type_pred(v, self.connected_resources_types)
        ]
        self.excluded_vertices = [
            v
            for v in self.vertices_under_resource_types + self.vertices_under_connected_resources_types
            if v in exclude_vertices
        ]

    def get_operation(self, graph_connector: DiGraph) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        raise NotImplementedError

    def _get_operation(self, *args: Any, **kwargs: Any):
        raise NotImplementedError
