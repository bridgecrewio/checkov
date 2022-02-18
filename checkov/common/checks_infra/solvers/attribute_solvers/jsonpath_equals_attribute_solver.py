from typing import List, Optional, Any, Dict

from checkov.common.checks_infra.solvers.attribute_solvers.base_attribute_solver import BaseAttributeSolver
from checkov.common.graph.checks_infra.enums import Operators
from jsonpath_ng.ext import parse


class JsonpathEqualsAttributeSolver(BaseAttributeSolver):
    operator = Operators.JSONPATH_EQUALS

    def __init__(self, resource_types: List[str], attribute: Optional[str], value: Any) -> None:
        super().__init__(resource_types=resource_types,
                         attribute=attribute, value=value)

    def _get_operation(self, vertex: Dict[str, Any], attribute: Optional[str]) -> bool:
        return str(vertex.get(attribute)) == str(self.value)

    def get_operation(self, vertex: Dict[str, Any]) -> bool:
        if self.attribute:
            attribute_matches = []
            parsed_attr = parse(self.attribute)
            for match in parsed_attr.find(vertex):
                full_path = str(match.full_path)
                if full_path not in vertex:
                    vertex[full_path] = match.value

                attribute_matches.append(full_path)

            return self.resource_type_pred(vertex, self.resource_types) and len(attribute_matches) > 0 and all(
                self._get_operation(vertex=vertex, attribute=attr) for attr in attribute_matches
            )

        return self.resource_type_pred(vertex, self.resource_types) and self._get_operation(
            vertex=vertex, attribute=self.attribute
        )
