from typing import List, Optional, Any, Dict

from checkov.common.checks_infra.solvers.attribute_solvers.jsonpath_equals_attribute_solver import JsonpathEqualsAttributeSolver
from checkov.common.graph.checks_infra.enums import Operators


class JsonpathNotEqualsAttributeSolver(JsonpathEqualsAttributeSolver):
    operator = Operators.JSONPATH_NOT_EQUALS

    def __init__(self, resource_types: List[str], attribute: Optional[str], value: Any) -> None:
        super().__init__(resource_types=resource_types, attribute=attribute, value=value)

    def get_operation(self, vertex: Dict[str, Any]) -> bool:
        if self.attribute:
            attribute_matches = self._get_attribute_matches(vertex)
            if not attribute_matches:  # the jsonpath is not found, so the check passes
                return True

            return self.resource_type_pred(vertex, self.resource_types) and all(
                self._get_operation(vertex=vertex, attribute=attr) for attr in attribute_matches
            )

        return self.resource_type_pred(vertex, self.resource_types) and self._get_operation(
            vertex=vertex, attribute=self.attribute
        )

    def _get_operation(self, vertex: Dict[str, Any], attribute: Optional[str]) -> bool:
        return not super()._get_operation(vertex, attribute)
