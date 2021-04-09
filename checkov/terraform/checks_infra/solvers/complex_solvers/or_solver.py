from checkov.common.graph.checks_infra.enums import Operators
from checkov.terraform.checks_infra.solvers.complex_solvers.base_complex_solver import BaseComplexSolver
from functools import reduce
from operator import or_


class OrSolver(BaseComplexSolver):
    operator = Operators.OR

    def __init__(self, solvers, resource_types):
        super().__init__(solvers, resource_types)

    def _get_operation(self, *args):
        return reduce(or_, args)

    def get_operation(self, vertex):
        for i, solver in enumerate(self.solvers):
            pred_result = solver.get_operation(vertex)
            if pred_result:
                return pred_result
        return False
