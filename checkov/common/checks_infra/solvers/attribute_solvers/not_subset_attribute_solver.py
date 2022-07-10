from typing import List, Optional, Any, Dict

from checkov.common.checks_infra.solvers.attribute_solvers.subset_attribute_solver import SubsetAttributeSolver
from checkov.common.graph.checks_infra.enums import Operators


class NotSubsetAttributeSolver(SubsetAttributeSolver):
    operator = Operators.NOT_SUBSET  # noqa: CCE003  # a static attribute

    def _get_operation(self, vertex: Dict[str, Any], attribute: Optional[str]) -> bool:  # type:ignore[override]
        return not super()._get_operation(vertex, attribute)
