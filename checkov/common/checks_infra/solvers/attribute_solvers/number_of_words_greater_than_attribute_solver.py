from typing import Optional, Any, Dict

from checkov.common.checks_infra.solvers.attribute_solvers.base_number_of_words_attribute_solver import \
    BaseNumberOfWordsAttributeSolver  # checkov:skip=CKV_SECRET_256
from checkov.common.graph.checks_infra.enums import Operators


class NumberOfWordsGreaterThanAttributeSolver(BaseNumberOfWordsAttributeSolver):
    operator = Operators.NUMBER_OF_WORDS_GREATER_THAN  # noqa: CCE003  # a static attribute

    def _get_operation(self, vertex: Dict[str, Any], attribute: Optional[str]) -> bool:
        attr = vertex.get(attribute)  # type:ignore[arg-type]  # due to attribute can be None

        if not self._validate_vertex_value(attr):
            return False

        num_of_words = self._get_number_of_words(attr)
        value_numeric = self._numerize_value()

        if value_numeric is None:
            return False

        return num_of_words > value_numeric
