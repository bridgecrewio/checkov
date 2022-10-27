from typing import Optional, Any, Dict
from collections.abc import Sized
from checkov.common.checks_infra.solvers.attribute_solvers.base_attribute_solver import BaseAttributeSolver
from checkov.common.graph.checks_infra.enums import Operators
from checkov.common.util.type_forcers import force_int


class LengthEqualsAttributeSolver(BaseAttributeSolver):
    operator = Operators.LENGTH_EQUALS  # noqa: CCE003  # a static attribute

    def _get_operation(self, vertex: Dict[str, Any], attribute: Optional[str]) -> bool:
        if vertex.get(attribute) is None:  # type:ignore[arg-type]  # due to attribute can be None
            return False

        attr = vertex.get(attribute)  # type:ignore[arg-type]  # due to attribute can be None
        if isinstance(attr, Sized):
            return len(attr) == force_int(self.value)

        return False
