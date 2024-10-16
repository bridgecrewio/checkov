from __future__ import annotations

from checkov.common.graph.checks_infra.enums import Operators
from checkov.common.checks_infra.solvers.resource_solvers.base_resource_solver import BaseResourceSolver


class ExistsResourcerSolver(BaseResourceSolver):
    operator = Operators.EXISTS  # noqa: CCE003  # a static attribute

    def get_operation(self, resource_type: str | None) -> bool:
        return resource_type in self.resource_types

    def _handle_result(self, result: bool, data: dict[str, str]) -> None:
        # The exists operator means that all resources that are not in the allowlist should fail,
        # and existed resources that are in the allowlist should pass, as they are the only resources allowed
        if result:
            self._passed_vertices.append(data)
        else:
            self._failed_vertices.append(data)
