from typing import List, Optional, Any, Dict

from checkov.common.checks_infra.solvers.attribute_solvers.jsonpath_exists_attribute_solver import JsonpathExistsAttributeSolver
from checkov.common.graph.checks_infra.enums import Operators


class JsonpathNotExistsAttributeSolver(JsonpathExistsAttributeSolver):
    operator = Operators.JSONPATH_NOT_EXISTS

    def __init__(self, resource_types: List[str], attribute: Optional[str], value: Any) -> None:
        super().__init__(resource_types=resource_types,
                         attribute=attribute, value=value)

    def get_operation(self, vertex: Dict[str, Any]) -> bool:
        if self.attribute:
            attribute_matches = self._get_attribute_matches(vertex)
            return len(attribute_matches) == 0

        return super().get_operation(vertex)

    def _get_operation(self, vertex: Dict[str, Any], attribute: Optional[str]) -> bool:
        return not super()._get_operation(vertex, attribute)
