from typing import Optional, Any, Dict

from checkov.common.graph.checks_infra.enums import Operators
from checkov.common.checks_infra.solvers.attribute_solvers.base_attribute_solver import BaseAttributeSolver
from checkov.common.util.type_forcers import force_float


class GreaterThanAttributeSolver(BaseAttributeSolver):
    operator = Operators.GREATER_THAN  # noqa: CCE003  # a static attribute

    def _get_operation(self, vertex: Dict[str, Any], attribute: Optional[str]) -> bool:
        vertex_attr = vertex.get(attribute)  # type:ignore[arg-type]  # due to attribute can be None
        attr_float = force_float(vertex_attr)
        value_float = force_float(self.value)

        if vertex_attr is None:
            return False
        elif attr_float and value_float:
            return attr_float > value_float
        else:
            return str(vertex_attr) > str(self.value)
