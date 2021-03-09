from checkov.graph.terraform.checks.checks_infra.enums import SolverType
from checkov.graph.terraform.checks.checks_infra.solvers.base_solver import BaseSolver


class BaseComplexSolver(BaseSolver):
    operator = ''

    def __init__(self, queries, resource_types):
        if queries is None:
            queries = []
        self.queries = queries
        self.resource_types = resource_types
        super().__init__(SolverType.COMPLEX)

    def run_query(self, graph_connector):
        # TODO
        raise NotImplementedError

    def get_operation(self, *args):
        # TODO
        raise NotImplementedError

    def _get_operation(self, *args):
        pass
