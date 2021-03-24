from checkov.graph.checks.checks_infra.solvers.base_solver import BaseSolver
from checkov.graph.checks.checks_infra.enums import SolverType


class BaseFilterSolver(BaseSolver):
    operator = ''

    def __init__(self, resource_types, query_attribute, query_value):
        super().__init__(SolverType.FILTER)
        self.resource_types = resource_types
        self.query_attribute = query_attribute
        self.query_value = query_value
        self.vertices = []

    def get_operation(self, *args, **kwargs):
        raise NotImplementedError()

    def _get_operation(self, *args, **kwargs):
        raise NotImplementedError()

    def run(self, graph_connector):
        raise NotImplementedError()


