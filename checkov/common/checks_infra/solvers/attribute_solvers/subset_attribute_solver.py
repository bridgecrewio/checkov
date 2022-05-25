from typing import List, Optional, Any, Dict, Set

from checkov.common.graph.checks_infra.enums import Operators
from checkov.common.checks_infra.solvers.attribute_solvers.base_attribute_solver import BaseAttributeSolver


class SubsetAttributeSolver(BaseAttributeSolver):
    operator = Operators.SUBSET

    def __init__(self, resource_types: List[str], attribute: Optional[str], value: Any) -> None:
        super().__init__(resource_types=resource_types,
                         attribute=attribute, value=SubsetAttributeSolver.to_set(value))

    def _get_operation(self, vertex: Dict[str, Any], attribute: Optional[str]) -> bool:
        attr_val = SubsetAttributeSolver.to_set(vertex.get(attribute))  # type:ignore[arg-type]  # due to attribute can be None
        return attr_val.issubset(self.value)

    @staticmethod
    def to_set(value: Any) -> Set[Any]:
        if isinstance(value, set):
            return value
        elif isinstance(value, (list, dict)):
            return set(value)
        else:
            return {value}
