from __future__ import annotations

from abc import abstractmethod
from typing import Any, Callable, TYPE_CHECKING

from networkx import DiGraph

import concurrent.futures

from concurrent.futures import ThreadPoolExecutor

from checkov.common.graph.checks_infra.enums import SolverType
from checkov.common.graph.checks_infra.solvers.base_solver import BaseSolver
from checkov.common.graph.graph_builder import CustomAttributes

if TYPE_CHECKING:
    from checkov.common.typing import LibraryGraph


class BaseResourceSolver(BaseSolver):
    def __init__(self, resource_types: list[str]) -> None:
        super().__init__(SolverType.RESOURCE)
        self.resource_types = resource_types
        self.vertices: list[dict[str, Any]] = []
        self._passed_vertices: list[dict[str, Any]] = []
        self._failed_vertices: list[dict[str, Any]] = []
        self._unknown_vertices: list[dict[str, Any]] = []

    @abstractmethod
    def get_operation(self, resource_type: str) -> bool:
        raise NotImplementedError()

    def _get_operation(self, *args: Any, **kwargs: Any) -> Callable[..., bool]:
        # not needed
        return lambda: True

    @abstractmethod
    def _handle_result(self, result: bool, data: dict[str, str]) -> None:
        raise NotImplementedError()

    def run(
            self, graph_connector: LibraryGraph
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
        executer = ThreadPoolExecutor()
        jobs = []

        if isinstance(graph_connector, DiGraph):
            for _, data in graph_connector.nodes(data=True):
                jobs.append(executer.submit(self._process_node, data))

            concurrent.futures.wait(jobs)
            return self._passed_vertices, self._failed_vertices, self._unknown_vertices

        for _, data in graph_connector.nodes():
            result = self.get_operation(resource_type=data.get(CustomAttributes.RESOURCE_TYPE))
            self._handle_result(result, data)

        return self._passed_vertices, self._failed_vertices, self._unknown_vertices

    def _process_node(self, data: dict[str, str]) -> None:
        result = self.get_operation(data.get(CustomAttributes.RESOURCE_TYPE))  # type:ignore[arg-type]
        # A None indicate for UNKNOWN result - the vertex shouldn't be added to the passed or the failed vertices
        self._handle_result(result, data)
