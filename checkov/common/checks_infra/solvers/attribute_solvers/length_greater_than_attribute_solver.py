from typing import Optional, Any, Dict
from collections.abc import Sized
from checkov.common.checks_infra.solvers.attribute_solvers.base_attribute_solver import BaseAttributeSolver
from checkov.common.graph.checks_infra.enums import Operators
from checkov.common.util.type_forcers import force_int


class LengthGreaterThanAttributeSolver(BaseAttributeSolver):
    operator = Operators.LENGTH_GREATER_THAN  # noqa: CCE003  # a static attribute

    def _get_operation(self, vertex: Dict[str, Any], attribute: Optional[str]) -> bool:
        attr = vertex.get(attribute)  # type:ignore[arg-type]  # due to attribute can be None
        if attr is None:
            return False

        value_int = force_int(self.value)

        if value_int is None:
            return False
        if isinstance(attr, Sized):
            return len(attr) > value_int

        return False
