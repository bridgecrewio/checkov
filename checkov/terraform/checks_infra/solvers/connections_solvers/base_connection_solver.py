from abc import ABC

from networkx import DiGraph

from checkov.common.graph.checks_infra.enums import SolverType
from checkov.common.graph.checks_infra.solvers.base_solver import BaseSolver


class BaseConnectionSolver(BaseSolver, ABC):

    operator = ''

    def __init__(self, resource_types, connected_resources_types, vertices_under_resource_types=None, vertices_under_connected_resources_types=None):
        super().__init__(SolverType.CONNECTION)
        self.resource_types = resource_types
        self.connected_resources_types = connected_resources_types
        self.vertices_under_resource_types = vertices_under_resource_types or []
        self.vertices_under_connected_resources_types = vertices_under_connected_resources_types or []

    def run(self, graph_connector: DiGraph):
        raise NotImplementedError()

    def is_associated_edge(self, origin_type: str, destination_type: str):
        return (origin_type in self.resource_types and destination_type in self.connected_resources_types) or (
                    origin_type in self.connected_resources_types and destination_type in self.resource_types)

    def is_associated_vertex(self, vertex_type: str):
        return vertex_type in self.resource_types or vertex_type in self.connected_resources_types
