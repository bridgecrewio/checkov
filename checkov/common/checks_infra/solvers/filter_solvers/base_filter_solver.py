from __future__ import annotations

from typing import Any, Callable

from networkx import DiGraph

from checkov.common.graph.checks_infra.enums import SolverType
from checkov.common.graph.checks_infra.solvers.base_solver import BaseSolver


class BaseFilterSolver(BaseSolver):
    def __init__(self, resource_types: list[str], attribute: str | None, value: Any) -> None:
        super().__init__(SolverType.FILTER)
        self.resource_types = resource_types
        self.attribute = attribute
        self.value = value
        self.vertices: list[dict[str, Any]] = []

    def get_operation(self, *args: Any, **kwargs: Any) -> bool:
        raise NotImplementedError()

    def _get_operation(self, *args: Any, **kwargs: Any) -> Callable[..., bool]:
        raise NotImplementedError()

    def run(self, graph_connector: DiGraph) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        raise NotImplementedError()
