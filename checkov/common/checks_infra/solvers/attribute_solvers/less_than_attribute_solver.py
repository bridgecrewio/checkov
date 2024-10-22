from typing import Optional, Any, Dict

from checkov.common.graph.checks_infra.enums import Operators
from .greater_than_or_equal_attribute_solver import GreaterThanOrEqualAttributeSolver


class LessThanAttributeSolver(GreaterThanOrEqualAttributeSolver):
    operator = Operators.LESS_THAN  # noqa: CCE003  # a static attribute

    def _get_operation(self, vertex: Dict[str, Any], attribute: Optional[str]) -> bool:
        if vertex.get(attribute) is None:  # type:ignore[arg-type]  # due to attribute can be None
            return False

        return not super()._get_operation(vertex, attribute)
