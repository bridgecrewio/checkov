from typing import List, Optional, Any, Dict

from checkov.common.graph.checks_infra.enums import Operators
from .regex_match_attribute_solver import RegexMatchAttributeSolver


class NotRegexMatchAttributeSolver(RegexMatchAttributeSolver):
    operator = Operators.NOT_REGEX_MATCH  # noqa: CCE003  # a static attribute

    def _get_operation(self, vertex: Dict[str, Any], attribute: Optional[str]) -> bool:  # type:ignore[override]
        return not super()._get_operation(vertex, attribute)
