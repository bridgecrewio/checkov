from typing import Optional, Any, Dict, Collection
from collections.abc import Iterable
from checkov.common.graph.checks_infra.enums import Operators
from checkov.common.checks_infra.solvers.attribute_solvers.base_attribute_solver import BaseAttributeSolver


class IntersectsAttributeSolver(BaseAttributeSolver):
    operator = Operators.INTERSECTS  # noqa: CCE003  # a static attribute

    def _get_operation(self, vertex: Dict[str, Any], attribute: Optional[str]) -> bool:
        attr = vertex.get(attribute)  # type:ignore[arg-type]  # due to attribute can be None

        if isinstance(self.value, str) and isinstance(attr, Iterable):
            return self.value in attr

        if isinstance(self.value, Collection) and isinstance(attr, Iterable):
            return any(i in self.value for i in attr)

        return False
