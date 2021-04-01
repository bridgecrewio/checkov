from checkov.common.graph.checks_infra.enums import Operators
from checkov.terraform.checks_infra.solvers.complex_solvers.base_complex_solver import BaseComplexSolver
from functools import reduce
from operator import and_


class AndSolver(BaseComplexSolver):
    operator = Operators.AND

    def __init__(self, solvers, resource_types):
        super().__init__(solvers, resource_types)

    def _get_operation(self, *args):
        return reduce(and_, args)

    def get_operation(self, vertex):
        for i, solver in enumerate(self.solvers):
            pred_result = solver.get_operation(vertex)
            if not pred_result:
                return pred_result
        return True
