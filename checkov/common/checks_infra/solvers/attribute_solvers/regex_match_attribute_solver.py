import logging
import re
from typing import List, Optional, Any, Dict

from checkov.common.graph.checks_infra.enums import Operators
from checkov.common.checks_infra.solvers.attribute_solvers.base_attribute_solver import BaseAttributeSolver


class RegexMatchAttributeSolver(BaseAttributeSolver):
    operator = Operators.REGEX_MATCH

    def __init__(self, resource_types: List[str], attribute: Optional[str], value: Any) -> None:
        super().__init__(resource_types=resource_types,
                         attribute=attribute, value=value)

    def _get_operation(self, vertex: Dict[str, Any], attribute: Optional[str]) -> bool:
        attr = vertex.get(attribute)  # type:ignore[arg-type]  # due to attribute can be None
        try:
            return re.match(str(self.value), str(attr)) is not None
        except re.error as e:
            logging.warn(f'failed to run regex {self.value} for attribute: {attr}, ', e)
            return False
