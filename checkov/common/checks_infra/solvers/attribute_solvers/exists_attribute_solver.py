from typing import List, Optional, Any, Dict

from checkov.common.graph.checks_infra.enums import Operators
from checkov.common.checks_infra.solvers.attribute_solvers.base_attribute_solver import BaseAttributeSolver


class ExistsAttributeSolver(BaseAttributeSolver):
    operator = Operators.EXISTS  # noqa: CCE003  # a static attribute

    def __init__(self, resource_types: List[str], attribute: Optional[str], value: Any) -> None:
        super().__init__(resource_types=resource_types, attribute=attribute, value=value)

    def _get_operation(self, vertex: Dict[str, Any], attribute: Optional[str]) -> bool:  # type:ignore[override]
        return vertex.get(attribute) is not None  # type:ignore[arg-type]  # due to attribute can be None
