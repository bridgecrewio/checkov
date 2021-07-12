import json
from typing import List, Optional, Any, Dict

from checkov.common.graph.checks_infra.enums import Operators
from checkov.common.checks_infra.solvers.attribute_solvers.base_attribute_solver import BaseAttributeSolver


class ContainsAttributeSolver(BaseAttributeSolver):
    operator = Operators.CONTAINS

    def __init__(self, resource_types: List[str], attribute: Optional[str], value: Any) -> None:
        super().__init__(resource_types=resource_types, attribute=attribute, value=value)

    def _get_operation(self, vertex: Dict[str, Any], attribute: Optional[str]) -> bool:
        att = vertex.get(attribute, "")
        if not isinstance(att, str):
            att = json.dumps(att)
        return self.value in att
