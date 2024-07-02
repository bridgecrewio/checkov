from __future__ import annotations


from checkov.common.graph.checks_infra.enums import Operators
from checkov.common.checks_infra.solvers.resource_solvers.base_resource_solver import BaseResourceSolver


class ExistsResourcerSolver(BaseResourceSolver):
    operator = Operators.EXISTS  # noqa: CCE003  # a static attribute

    def get_operation(self, resource_type: str | None) -> bool:
        return resource_type in self.resource_types
