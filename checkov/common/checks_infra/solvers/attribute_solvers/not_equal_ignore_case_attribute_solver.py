from typing import Optional, Any, Dict

from checkov.common.graph.checks_infra.enums import Operators
from .equal_ignore_case_attribute_solver import EqualIgnoreCaseAttributeSolver


class NotEqualIgnoreCaseAttributeSolver(EqualIgnoreCaseAttributeSolver):
    operator = Operators.NOT_EQUAL_IGNORE_CASE  # noqa: CCE003  # a static attribute

    def _get_operation(self, vertex: Dict[str, Any], attribute: Optional[str]) -> bool:
        return not super()._get_operation(vertex, attribute)
