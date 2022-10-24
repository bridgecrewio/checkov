from typing import Optional, Any, Dict

from .length_equals_attribute_solver import LengthEqualsAttributeSolver
from checkov.common.graph.checks_infra.enums import Operators


class LengthNotEqualsAttributeSolver(LengthEqualsAttributeSolver):
    operator = Operators.LENGTH_NOT_EQUALS  # noqa: CCE003  # a static attribute

    def _get_operation(self, vertex: Dict[str, Any], attribute: Optional[str]) -> bool:
        return not super()._get_operation(vertex, attribute)
