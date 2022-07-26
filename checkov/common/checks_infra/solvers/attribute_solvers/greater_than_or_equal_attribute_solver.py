from typing import List, Optional, Any, Dict

from checkov.common.graph.checks_infra.enums import Operators
from checkov.common.checks_infra.solvers.attribute_solvers.base_attribute_solver import BaseAttributeSolver
from checkov.common.util.type_forcers import force_float


class GreaterThanOrEqualAttributeSolver(BaseAttributeSolver):
    operator = Operators.GREATER_THAN_OR_EQUAL  # noqa: CCE003  # a static attribute

    def _get_operation(self, vertex: Dict[str, Any], attribute: Optional[str]) -> bool:  # type:ignore[override]

        vertex_attr = vertex.get(attribute)  # type:ignore[arg-type]  # due to attribute can be None
        # if this value contains an underendered variable, then we cannot evaluate the check,
        # so return True (since we cannot return UNKNOWN)
        if self._is_variable_dependant(vertex_attr, vertex['source_']):
            return True
        attr_float = force_float(vertex_attr)
        value_float = force_float(self.value)

        if vertex_attr is None:
            return False
        elif attr_float and value_float:
            return attr_float >= value_float
        else:
            return str(vertex_attr) >= str(self.value)
