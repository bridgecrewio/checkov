from typing import List, Optional, Any, Dict

from checkov.common.graph.checks_infra.enums import Operators
from .starting_with_attribute_solver import StartingWithAttributeSolver


class NotStartingWithAttributeSolver(StartingWithAttributeSolver):
    operator = Operators.NOT_STARTING_WITH  # noqa: CCE003  # a static attribute

    def __init__(self, resource_types: List[str], attribute: Optional[str], value: Any) -> None:
        super().__init__(resource_types=resource_types, attribute=attribute, value=value)

    def _get_operation(self, vertex: Dict[str, Any], attribute: Optional[str]) -> bool:  # type:ignore[override]
        return not super()._get_operation(vertex, attribute)
