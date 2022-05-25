from typing import List, Optional, Any, Dict

from checkov.common.graph.checks_infra.enums import Operators
from checkov.common.checks_infra.solvers.attribute_solvers.base_attribute_solver import BaseAttributeSolver


class EqualsAttributeSolver(BaseAttributeSolver):
    operator = Operators.EQUALS

    def __init__(self, resource_types: List[str], attribute: Optional[str], value: Any) -> None:
        super().__init__(resource_types=resource_types,
                         attribute=attribute, value=value)

    def _get_operation(self, vertex: Dict[str, Any], attribute: Optional[str]) -> bool:
        attr_val = vertex.get(attribute)  # type:ignore[arg-type]  # due to attribute can be None
        if type(attr_val) == bool or type(self.value) == bool:
            # handle cases like str(False) == "false"
            # generally self.value will be a string, but could be a bool if the policy was created straight from json
            return str(attr_val).lower() == str(self.value).lower()
        else:
            return str(attr_val) == str(self.value)
