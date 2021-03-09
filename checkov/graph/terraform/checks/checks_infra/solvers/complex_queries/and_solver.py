from checkov.graph.terraform.checks.checks_infra.solvers.complex_queries.base_complex_query import BaseComplexSolver


class AndSolver(BaseComplexSolver):
    operator = 'and'

    def __init__(self, queries, resource_types):
        super().__init__(queries, resource_types)

    def _get_operation(self, *args):
        # TODO
        raise NotImplementedError
