from __future__ import annotations

from typing import Any, TYPE_CHECKING

from checkov.common.graph.checks_infra.enums import Operators
from checkov.common.checks_infra.solvers.attribute_solvers.base_attribute_solver import BaseAttributeSolver
from checkov.common.util.type_forcers import force_int

if TYPE_CHECKING:
    from typing_extensions import TypeGuard


class BaseNumberOfWordsAttributeSolver(BaseAttributeSolver):
    operator = Operators.NUMBER_OF_WORDS_GREATER_THAN  # noqa: CCE003  # a static attribute

    def _validate_vertex_value(self, attr: Any) -> TypeGuard[str]:
        return isinstance(attr, str)

    def _get_number_of_words(self, attr: str) -> int:
        return len(attr.split())

    def _numerize_value(self) -> int | None:
        return force_int(self.value)

    def _get_operation(self, vertex: dict[str, Any], attribute: str | None) -> bool:
        attr = vertex.get(attribute)  # type:ignore[arg-type]  # due to attribute can be None
        return self._validate_vertex_value(attr)
