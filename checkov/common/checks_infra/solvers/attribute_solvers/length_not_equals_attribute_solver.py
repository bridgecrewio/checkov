from typing import List, Optional, Any, Dict

from .length_equals_attribute_solver import LengthEqualsAttributeSolver
from checkov.common.graph.checks_infra.enums import Operators


class LengthNotEqualsAttributeSolver(LengthEqualsAttributeSolver):
    operator = Operators.LENGTH_NOT_EQUALS

    def __init__(self, resource_types: List[str], attribute: Optional[str], value: Any) -> None:
        super().__init__(resource_types=resource_types, attribute=attribute, value=value)

    def _get_operation(self, vertex: Dict[str, Any], attribute: Optional[str]) -> bool:
        return not super()._get_operation(vertex, attribute)
