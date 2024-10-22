from typing import Any, Callable, List, Dict

from checkov.common.graph.checks_infra.enums import Operators
from checkov.common.checks_infra.solvers.filter_solvers.base_filter_solver import BaseFilterSolver


class WithinFilterSolver(BaseFilterSolver):
    operator = Operators.WITHIN  # noqa: CCE003  # a static attribute

    def __init__(self, resource_types: List[str], attribute: str, value: Any) -> None:
        super().__init__(resource_types=resource_types, attribute=attribute, value=value)

    def get_operation(self, *args: Any, **kwargs: Any) -> bool:
        return self._get_operation()(*args)

    def _get_operation(self, *args: Any, **kwargs: Any) -> Callable[..., bool]:
        def op(check: Dict[str, Any]) -> bool:
            if not self.attribute:
                return False

            val = check.get(self.attribute)
            return bool(val) and (val in self.value)
        return op
