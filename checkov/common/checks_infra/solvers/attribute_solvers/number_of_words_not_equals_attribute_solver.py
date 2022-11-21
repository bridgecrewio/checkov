from typing import Optional, Any, Dict

from checkov.common.graph.checks_infra.enums import Operators
from checkov.common.checks_infra.solvers.attribute_solvers.number_of_words_equals_attribute_solver import NumberOfWordsEqualsAttributeSolver


class NumberOfWordsNotEqualsAttributeSolver(NumberOfWordsEqualsAttributeSolver):
    operator = Operators.NUMBER_OF_WORDS_NOT_EQUALS  # noqa: CCE003  # a static attribute

    def _get_operation(self, vertex: Dict[str, Any], attribute: Optional[str]) -> bool:
        return not super()._get_operation(vertex, attribute)
