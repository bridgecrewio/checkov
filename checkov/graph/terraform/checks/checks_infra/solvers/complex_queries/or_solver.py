from checkov.graph.terraform.checks.checks_infra.solvers.complex_queries.base_complex_query import BaseComplexSolver


class OrSolver(BaseComplexSolver):
    operator = 'or'

    def __init__(self, queries, resource_types):
        super().__init__(queries, resource_types)

    def _get_operation(self, *args):
        # TODO
        raise NotImplementedError
