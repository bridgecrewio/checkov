from typing import Optional, Any, Dict, List
from checkov.common.checks_infra.solvers.attribute_solvers.base_attribute_solver import BaseAttributeSolver
from checkov.common.graph.checks_infra.enums import Operators
from checkov.common.util.type_forcers import force_int


class RangeIncludesAttributeSolver(BaseAttributeSolver):
    operator = Operators.RANGE_INCLUDES  # noqa: CCE003  # a static attribute

    def __init__(
        self, resource_types: List[str], attribute: Optional[str], value: Any, is_jsonpath_check: bool = False
    ) -> None:
        super().__init__(resource_types, attribute, force_int(value), is_jsonpath_check)

    def _get_operation(self, vertex: Dict[str, Any], attribute: Optional[str]) -> bool:
        if vertex.get(attribute) is None:  # type:ignore[arg-type]  # due to attribute can be None
            return False

        attr = vertex.get(attribute)  # type:ignore[arg-type]  # due to attribute can be None

        # expects one of the following values:
        # - an actual int
        # - a string that parses to an int
        # - *
        # - a string range like '1000-2000'

        if attr == '*':
            return True

        try:
            attr = force_int(attr)
            return attr == self.value
        except ValueError as e:
            if '-' in attr:
                try:
                    [start, end] = [force_int(a for a in attr.split('-'))]
                    return start <= self.value <= end
                except ValueError as e:
                    # Occurs if there are not two entries or if one is not an int, in which case we just give up
                    pass

        return False
