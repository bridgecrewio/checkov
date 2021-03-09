from checkov.graph.terraform.checks.checks_infra.enums import SolverType
from checkov.graph.terraform.checks.checks_infra.solvers.base_solver import BaseSolver


class BaseAttributeSolver(BaseSolver):
    operator = ''

    def __init__(self, resource_types, query_attribute, query_value):
        super().__init__(SolverType.ATTRIBUTE)
        self.resource_types = resource_types
        self.query_attribute = query_attribute
        self.query_value = query_value

    def run_query(self, graph_connector):
        # TODO
        raise NotImplementedError

    def get_operation(self, *args):
        # TODO
        raise NotImplementedError

    def get_negative_operation(self, *args):
        # TODO
        raise NotImplementedError

    def _get_operation(self, *args):
        raise NotImplementedError

