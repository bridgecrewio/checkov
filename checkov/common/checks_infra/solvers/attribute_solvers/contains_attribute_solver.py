import json
import logging
from typing import Optional, Any, Dict

from checkov.common.graph.checks_infra.enums import Operators
from checkov.common.checks_infra.solvers.attribute_solvers.base_attribute_solver import BaseAttributeSolver
from checkov.common.resource_code_logger_filter import add_resource_code_filter_to_logger

logger = logging.getLogger(__name__)
add_resource_code_filter_to_logger(logger)


class ContainsAttributeSolver(BaseAttributeSolver):
    operator = Operators.CONTAINS  # noqa: CCE003  # a static attribute

    def _get_operation(self, vertex: Dict[str, Any], attribute: Optional[str]) -> bool:
        att = vertex.get(attribute, "{}")  # type:ignore[arg-type]  # due to attribute can be None
        att = "{}" if att is None else att
        if isinstance(att, str):
            try:
                att = json.loads(att.replace("'", '"'))
            except ValueError:
                pass
        if isinstance(att, dict):
            return self.value in att or any(self.value in val for val in att.values() if type(val) in [str, list, set, dict])
        return self.value in att
