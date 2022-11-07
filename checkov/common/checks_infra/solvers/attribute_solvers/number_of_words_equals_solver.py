from typing import Optional, Any, Dict

from checkov.common.graph.checks_infra.enums import Operators
from checkov.common.checks_infra.solvers.attribute_solvers.base_attribute_solver import BaseAttributeSolver
from checkov.common.util.type_forcers import force_int


class NumberOfWordsEqualsAttributeSolver(BaseAttributeSolver):
    operator = Operators.NUMBER_OF_WORDS_EQUALS  # noqa: CCE003  # a static attribute

    def _get_operation(self, vertex: Dict[str, Any], attribute: Optional[str]) -> bool:
        vertex_attr = vertex.get(attribute)  # type:ignore[arg-type]  # due to attribute can be None

        if not isinstance(vertex_attr, str):
            return False
        words = vertex_attr.split()
        value_numeric = force_int(self.value)

        return len(words) == value_numeric
