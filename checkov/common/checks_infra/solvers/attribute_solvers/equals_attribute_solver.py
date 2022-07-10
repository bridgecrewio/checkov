from typing import List, Optional, Any, Dict

from checkov.common.graph.checks_infra.enums import Operators
from checkov.common.checks_infra.solvers.attribute_solvers.base_attribute_solver import BaseAttributeSolver


class EqualsAttributeSolver(BaseAttributeSolver):
    operator = Operators.EQUALS  # noqa: CCE003  # a static attribute

    def _get_operation(self, vertex: Dict[str, Any], attribute: Optional[str]) -> bool:  # type:ignore[override]
        attr_val = vertex.get(attribute)  # type:ignore[arg-type]  # due to attribute can be None
        # if this value contains an underendered variable, then we cannot evaluate the check,
        # so return True (since we cannot return UNKNOWN)
        # handle edge cases in some policies that explicitly look for blank values
        if self.value != '' and self._is_variable_dependant(attr_val, vertex['source_']):
            return True
        if type(attr_val) == bool or type(self.value) == bool:
            # handle cases like str(False) == "false"
            # generally self.value will be a string, but could be a bool if the policy was created straight from json
            return str(attr_val).lower() == str(self.value).lower()
        elif (isinstance(attr_val, list) and isinstance(self.value, list)) or (isinstance(attr_val, dict) and isinstance(self.value, dict)):
            return attr_val == self.value
        else:
            return str(attr_val) == str(self.value)
