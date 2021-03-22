from checkov.graph.checks.checks_infra.enums import SolverType
from checkov.graph.checks.checks_infra.solvers.base_solver import BaseSolver


class BaseComplexSolver(BaseSolver):
    operator = ''

    def __init__(self, queries, resource_types):
        if queries is None:
            queries = []
        self.queries = queries
        self.resource_types = resource_types
        super().__init__(SolverType.COMPLEX)

    def get_operation(self, *args, **kwargs):
        raise NotImplementedError()

    def _get_operation(self, *args, **kwargs):
        raise NotImplementedError()

    def run(self, graph_connector):
        raise NotImplementedError()
