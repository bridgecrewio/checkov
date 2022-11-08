from typing import Optional, Any, Dict

from checkov.common.graph.checks_infra.enums import Operators
from checkov.common.checks_infra.solvers.attribute_solvers.base_attribute_solver import BaseAttributeSolver
from checkov.common.util.type_forcers import force_int


class BaseNumberOfWordsAttributeSolver(BaseAttributeSolver):
    operator = Operators.NUMBER_OF_WORDS_GREATER_THAN  # noqa: CCE003  # a static attribute

    def _validate_vertex_value(self, attr) -> [str]:
        return isinstance(attr, str)

    def _get_number_of_words(self, attr):
        return len(attr.split())

    def _numerize_value(self):
        return force_int(self.value)

    def _get_operation(self, vertex: Dict[str, Any], attribute: Optional[str]) -> bool:
        attr = vertex.get(attribute)
        return self._validate_vertex_value(attr)
