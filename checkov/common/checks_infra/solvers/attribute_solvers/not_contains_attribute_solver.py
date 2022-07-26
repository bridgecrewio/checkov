from typing import List, Optional, Any, Dict

from checkov.common.graph.checks_infra.enums import Operators
from .contains_attribute_solver import ContainsAttributeSolver


class NotContainsAttributeSolver(ContainsAttributeSolver):
    operator = Operators.NOT_CONTAINS  # noqa: CCE003  # a static attribute

    def _get_operation(self, vertex: Dict[str, Any], attribute: Optional[str]) -> bool:  # type:ignore[override]
        return not super()._get_operation(vertex, attribute)
