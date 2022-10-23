from typing import Optional, Any, Dict

from checkov.common.graph.checks_infra.enums import Operators
from checkov.common.checks_infra.solvers.attribute_solvers.base_attribute_solver import BaseAttributeSolver


class EqualsIgnoreCaseAttributeSolver(BaseAttributeSolver):
    operator = Operators.EQUALS_IGNORE_CASE  # noqa: CCE003  # a static attribute

    def _get_operation(self, vertex: Dict[str, Any], attribute: Optional[str]) -> bool:
        attr_val = vertex.get(attribute)  # type:ignore[arg-type]  # due to attribute can be None
        # if this value contains an underendered variable, then we cannot evaluate the check,
        # so return True (since we cannot return UNKNOWN)
        # handle edge cases in some policies that explicitly look for blank values
        if self.value != '' and self._is_variable_dependant(attr_val, vertex['source_']):
            return True
        return str(attr_val).lower() == str(self.value).lower()
