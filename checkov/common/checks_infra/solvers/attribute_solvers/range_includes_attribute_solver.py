from typing import Optional, Any, Dict, List, Union
from checkov.common.checks_infra.solvers.attribute_solvers.base_attribute_solver import BaseAttributeSolver
from checkov.common.graph.checks_infra.enums import Operators
from checkov.common.util.type_forcers import force_int


class RangeIncludesAttributeSolver(BaseAttributeSolver):
    operator = Operators.RANGE_INCLUDES  # noqa: CCE003  # a static attribute

    def __init__(
            self, resource_types: List[str], attribute: Optional[str], value: Union[Any, List[Any]],
            is_jsonpath_check: bool = False
    ) -> None:
        super().__init__(resource_types, attribute, value, is_jsonpath_check)

    def _get_operation(self, vertex: Dict[str, Any], attribute: Optional[str]) -> bool:
        attr = vertex.get(attribute)  # type:ignore[arg-type]  # due to attribute can be None

        if attr is None:
            return False

        processed_value = self._handle_range_values(self.value)

        if isinstance(attr, list):
            return any(self._check_value(value, attr_val) for attr_val in attr for value in processed_value)

        return any(self._check_value(value, attr) for value in processed_value)

    def _handle_range_values(self, value: Union[Any, List[Any]]) -> List[Any]:
        # Convert value to a list if it's not already one to unify handling
        value_list = value if isinstance(value, list) else [value]

        # Process each item in the value list
        processed_value: List[Any] = []
        for v in value_list:
            if isinstance(v, str) and '-' in v:
                # Handle range strings
                start_str, end_str = v.split('-')
                start = force_int(start_str)
                end = force_int(end_str)
                if start is not None and end is not None:
                    processed_value.extend(range(start, end + 1))
            else:
                # Handle single values
                processed_value.append(force_int(v) if isinstance(v, (str, int)) else v)

        return processed_value

    def _check_value(self, value: Any, attr: Any) -> bool:
        # expects one of the following values:
        # - an actual int
        # - a string that parses to an int
        # - *
        # - a string range like '1000-2000'

        if attr == '*':
            return True

        if isinstance(attr, str) and attr.count("-") == 1:
            return self._check_range(value, attr)

        return bool(force_int(attr) == value)

    @staticmethod
    def _check_range(value: Any, range_str: str) -> bool:
        try:
            start, end = range_str.split("-")
            return bool(force_int(start) <= value <= force_int(end))
        except (TypeError, ValueError):
            # Occurs if there are not two entries or if one is not an int, in which case we just give up
            return False
