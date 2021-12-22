from typing import List, Any, Dict

from checkov.common.graph.checks_infra.enums import Operators
from checkov.common.graph.checks_infra.solvers.base_solver import BaseSolver
from checkov.common.checks_infra.solvers.complex_solvers.base_complex_solver import BaseComplexSolver
from functools import reduce
from operator import and_


class AndSolver(BaseComplexSolver):
    operator = Operators.AND

    def __init__(self, solvers: List[BaseSolver], resource_types: List[str]) -> None:
        super().__init__(solvers, resource_types)

    def _get_operation(self, *args: Any) -> Any:
        return reduce(and_, args)

    def get_operation(self, vertex: Dict[str, Any]) -> bool:
        for solver in self.solvers:
            if not solver.get_operation(vertex):
                return False
        return True
