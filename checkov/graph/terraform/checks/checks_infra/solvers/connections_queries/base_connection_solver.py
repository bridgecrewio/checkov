from checkov.graph.terraform.checks.checks_infra.solvers.base_solver import BaseSolver
from checkov.graph.terraform.checks.checks_infra.enums import SolverType


class BaseConnectionSolver(BaseSolver):

    operator = ''

    def __init__(self, resource_types, connected_resources_types, vertices_under_resource_types=None, vertices_under_connected_resources_types=None):
        super().__init__(SolverType.CONNECTION)
        self.resource_types = resource_types
        self.connected_resources_types = connected_resources_types
        self.vertices_under_resource_types = vertices_under_resource_types or []
        self.vertices_under_connected_resources_types = vertices_under_connected_resources_types or []

    def run_query(self, graph_connector):
        raise NotImplementedError

    def get_operation(self, *args):
        pass

    def _get_operation(self, *args):
        pass
