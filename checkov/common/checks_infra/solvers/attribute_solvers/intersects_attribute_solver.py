import logging
from typing import Optional, Any, Dict
from collections.abc import Sized
from checkov.common.graph.checks_infra.enums import Operators
from checkov.common.checks_infra.solvers.attribute_solvers.base_attribute_solver import BaseAttributeSolver

logger = logging.getLogger(__name__)


class IntersectsAttributeSolver(BaseAttributeSolver):
    operator = Operators.INTERSECTS  # noqa: CCE003  # a static attribute

    def _get_operation(self, vertex: Dict[str, Any], attribute: Optional[str]) -> bool:  # type:ignore[override]
        attr = vertex.get(attribute)  # type:ignore[arg-type]  # due to attribute can be None

        if isinstance(self.value, str) and isinstance(attr, Sized):
            return self.value in attr

        if type(self.value) in [list, set, dict] and type(attr) in [list, set, dict]:
            return any(i in self.value for i in attr)

        # if this value contains an underendered variable, then we cannot evaluate the check,
        # so return True (since we cannot return UNKNOWN)
        if self._is_variable_dependant(attr, vertex['source_']):
            return True

        return False
