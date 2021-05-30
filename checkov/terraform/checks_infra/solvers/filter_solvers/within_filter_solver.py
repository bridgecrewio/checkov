from typing import List, Any, Callable

from checkov.common.graph.checks_infra.enums import Operators
from checkov.terraform.checks_infra.solvers.filter_solvers.base_filter_solver import BaseFilterSolver


class WithinFilterSolver(BaseFilterSolver):
    operator = Operators.WITHIN

    def __init__(self, resource_types: List[str], attribute: str, value: Any) -> None:
        super().__init__(resource_types=resource_types, attribute=attribute, value=value)

    def get_operation(self, *args: Any, **kwargs: Any) -> bool:
        return self._get_operation()(*args)

    def _get_operation(self, *args: Any, **kwargs: Any) -> Callable[..., bool]:
        return lambda check: check.get(self.attribute) in self.value
