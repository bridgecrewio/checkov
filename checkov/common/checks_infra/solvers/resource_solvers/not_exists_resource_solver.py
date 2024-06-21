from __future__ import annotations

from typing import Any

from checkov.common.checks_infra.solvers.resource_solvers.exists_resource_solver import ExistsResourcerSolver
from checkov.common.graph.checks_infra.enums import Operators


class NotExistsResourcerSolver(ExistsResourcerSolver):
    operator = Operators.NOT_EXISTS  # noqa: CCE003  # a static attribute

    def get_operation(self, *args: Any, **kwargs: Any) -> bool:
        return not super().get_operation(*args, **kwargs)
