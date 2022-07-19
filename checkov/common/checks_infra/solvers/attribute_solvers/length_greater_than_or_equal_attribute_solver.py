from typing import Optional, Any, Dict

from .length_less_than_attribute_solver import LengthLessThanAttributeSolver
from checkov.common.graph.checks_infra.enums import Operators


class LengthGreaterThanOrEqualAttributeSolver(LengthLessThanAttributeSolver):
    operator = Operators.LENGTH_GREATER_THAN  # noqa: CCE003  # a static attribute

    def _get_operation(self, vertex: Dict[str, Any], attribute: Optional[str]) -> bool:  # type:ignore[override]
        return not super()._get_operation(vertex, attribute)
