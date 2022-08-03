from typing import List, Optional, Any, Dict

from checkov.common.graph.checks_infra.enums import Operators
from .greater_than_attribute_solver import GreaterThanAttributeSolver


class LessThanOrEqualAttributeSolver(GreaterThanAttributeSolver):
    operator = Operators.LESS_THAN_OR_EQUAL  # noqa: CCE003  # a static attribute

    def _get_operation(self, vertex: Dict[str, Any], attribute: Optional[str]) -> bool:  # type:ignore[override]
        if vertex.get(attribute) is None:  # type:ignore[arg-type]  # due to attribute can be None
            return False

        attr_val = vertex.get(attribute)  # type:ignore[arg-type]  # due to attribute can be None
        # if this value contains an underendered variable, then we cannot evaluate the check,
        # so return True (since we cannot return UNKNOWN)
        if self._is_variable_dependant(attr_val, vertex['source_']):
            return True

        return not super()._get_operation(vertex, attribute)
