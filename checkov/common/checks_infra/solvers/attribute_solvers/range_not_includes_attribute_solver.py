from typing import Optional, Any, Dict
from checkov.common.checks_infra.solvers.attribute_solvers.range_includes_attribute_solver import RangeIncludesAttributeSolver
from checkov.common.graph.checks_infra.enums import Operators


class RangeNotIncludesAttributeSolver(RangeIncludesAttributeSolver):
    operator = Operators.RANGE_NOT_INCLUDES  # noqa: CCE003  # a static attribute

    def _get_operation(self, vertex: Dict[str, Any], attribute: Optional[str]) -> bool:
        return not super()._get_operation(vertex, attribute)
