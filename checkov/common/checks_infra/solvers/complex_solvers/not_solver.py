from typing import List, Any, Dict, Optional

from checkov.common.graph.checks_infra.enums import Operators
from checkov.common.graph.checks_infra.solvers.base_solver import BaseSolver
from checkov.common.checks_infra.solvers.complex_solvers.base_complex_solver import BaseComplexSolver


class NotSolver(BaseComplexSolver):
    operator = Operators.NOT  # noqa: CCE003  # a static attribute

    def __init__(self, solvers: List[BaseSolver], resource_types: List[str]) -> None:
        if len(solvers) != 1:
            raise Exception('The "not" operator must have exactly one child')
        super().__init__(solvers, resource_types)

    def _get_operation(self, *args: Any, **kwargs: Any) -> Any:
        if len(args) != 1:
            raise Exception('The "not" operator must have exactly one child')
        return not args[0]

    def get_operation(self, vertex: Dict[str, Any]) -> Optional[bool]:
        result = self.solvers[0].get_operation(vertex)
        return None if result is None else not result
