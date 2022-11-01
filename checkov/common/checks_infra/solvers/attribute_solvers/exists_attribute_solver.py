from typing import Optional, Any, Dict

from checkov.common.graph.checks_infra.enums import Operators
from checkov.common.checks_infra.solvers.attribute_solvers.base_attribute_solver import BaseAttributeSolver


class ExistsAttributeSolver(BaseAttributeSolver):
    operator = Operators.EXISTS  # noqa: CCE003  # a static attribute
    is_value_attribute_check = False  # noqa: CCE003  # a static attribute

    def _get_operation(self, vertex: Dict[str, Any], attribute: Optional[str]) -> bool:
        return vertex.get(attribute) is not None  # type:ignore[arg-type]  # due to attribute can be None
