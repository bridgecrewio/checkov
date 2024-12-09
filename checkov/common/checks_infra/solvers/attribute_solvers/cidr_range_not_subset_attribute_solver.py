from typing import Optional, Any, Dict

from checkov.common.checks_infra.solvers.attribute_solvers.cidr_range_subset_attribute_solver import CIDRRangeSubsetAttributeSolver
from checkov.common.graph.checks_infra.enums import Operators


class CIDRRangeNotSubsetAttributeSolver(CIDRRangeSubsetAttributeSolver):
    operator = Operators.CIDR_RANGE_NOT_SUBSET  # noqa: CCE003  # a static attribute

    def _get_operation(self, vertex: Dict[str, Any], attribute: Optional[str]) -> bool:
        return not super()._get_operation(vertex, attribute)
