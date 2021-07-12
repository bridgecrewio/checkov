from typing import List, Optional, Any, Dict

from checkov.common.graph.checks_infra.enums import Operators
from .exists_attribute_solver import ExistsAttributeSolver


class NotExistsAttributeSolver(ExistsAttributeSolver):
    operator = Operators.NOT_EXISTS

    def __init__(self, resource_types: List[str], attribute: Optional[str], value: Any) -> None:
        super().__init__(resource_types=resource_types, attribute=attribute, value=value)

    def _get_operation(self, vertex: Dict[str, Any], attribute: Optional[str]) -> bool:
        return not super()._get_operation(vertex, attribute)
