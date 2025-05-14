from typing import Optional, Any, Dict
from collections.abc import Collection

import hcl2

from checkov.common.graph.checks_infra.enums import Operators
from checkov.common.checks_infra.solvers.attribute_solvers.base_attribute_solver import BaseAttributeSolver
from checkov.common.util.consts import START_LINE, END_LINE


class IsEmptyAttributeSolver(BaseAttributeSolver):
    operator = Operators.IS_EMPTY  # noqa: CCE003  # a static attribute

    def _get_operation(self, vertex: Dict[str, Any], attribute: Optional[str]) -> bool:
        attr = vertex.get(attribute)  # type:ignore[arg-type]  # due to attribute can be None

        if isinstance(attr, (list, Collection)):
            if len(attr) == 0 \
                    or (len(attr) == 2 and START_LINE in attr and END_LINE in attr) \
                    or (len(attr) == 2 and hcl2.START_LINE in attr and hcl2.END_LINE in attr):
                return True

        return False
