from typing import List, Optional, Any, Dict

from checkov.common.graph.checks_infra.enums import Operators
from .regex_match_attribute_solver import RegexMatchAttributeSolver


class NotRegexMatchAttributeSolver(RegexMatchAttributeSolver):
    operator = Operators.NOT_REGEX_MATCH

    def __init__(self, resource_types: List[str], attribute: Optional[str], value: Any) -> None:
        super().__init__(resource_types=resource_types, attribute=attribute, value=value)

    def _get_operation(self, vertex: Dict[str, Any], attribute: Optional[str]) -> bool:
        return not super()._get_operation(vertex, attribute)
