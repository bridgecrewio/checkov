from __future__ import annotations


from checkov.common.checks_infra.solvers.resource_solvers.exists_resource_solver import ExistsResourcerSolver
from checkov.common.graph.checks_infra.enums import Operators


class NotExistsResourcerSolver(ExistsResourcerSolver):
    operator = Operators.NOT_EXISTS  # noqa: CCE003  # a static attribute

    def get_operation(self, resource_type: str | None) -> bool:
        return not super().get_operation(resource_type)

    def _handle_result(self, result: bool, data: dict[str, str]) -> None:
        # The not_exists operator means that all resources that are not in the denylist should be ignored,
        # and existed resources that are in the denylist should fail
        if result:
            self._unknown_vertices.append(data)
        else:
            self._failed_vertices.append(data)
