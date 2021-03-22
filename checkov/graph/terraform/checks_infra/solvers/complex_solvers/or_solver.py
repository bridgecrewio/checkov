from checkov.graph.terraform.checks_infra.solvers.complex_solvers.base_complex_solver import BaseComplexSolver


class OrSolver(BaseComplexSolver):
    operator = 'or'

    def __init__(self, queries, resource_types):
        super().__init__(queries, resource_types)

    def _get_operation(self, *args):
        # TODO
        raise NotImplementedError
