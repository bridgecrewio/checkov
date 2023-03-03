from typing import Optional, Any, Dict

from checkov.common.graph.checks_infra.enums import Operators
from .equals_attribute_solver import EqualsAttributeSolver


class NotEqualsAttributeSolver(EqualsAttributeSolver):
    operator = Operators.NOT_EQUALS  # noqa: CCE003  # a static attribute

    def _get_operation(self, vertex: Dict[str, Any], attribute: Optional[str]) -> bool:
        return not super()._get_operation(vertex, attribute)
