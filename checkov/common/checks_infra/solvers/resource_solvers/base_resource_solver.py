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

    @abstractmethod
    def get_operation(self, resource_type: str) -> bool:
        raise NotImplementedError()

    def _get_operation(self, *args: Any, **kwargs: Any) -> Callable[..., bool]:
        # not needed
        return lambda: True

    def run(
        self, graph_connector: LibraryGraph
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
        executer = ThreadPoolExecutor()
        jobs = []
        passed_vertices: list[dict[str, Any]] = []
        failed_vertices: list[dict[str, Any]] = []
        unknown_vertices: list[dict[str, Any]] = []

        if isinstance(graph_connector, DiGraph):
            for _, data in graph_connector.nodes(data=True):
                jobs.append(executer.submit(self._process_node, data, passed_vertices, failed_vertices, unknown_vertices))

            concurrent.futures.wait(jobs)
            return passed_vertices, failed_vertices, unknown_vertices

        for _, data in graph_connector.nodes():
            result = self.get_operation(resource_type=data.get(CustomAttributes.RESOURCE_TYPE))
            if result:
                passed_vertices.append(data)
            else:
                failed_vertices.append(data)

        return passed_vertices, failed_vertices, []

    def _process_node(self, data: dict[str, str], passed_vartices: list[dict[str, Any]],
                      failed_vertices: list[dict[str, Any]], unknown_vertices: list[dict[str, Any]]) -> None:
        result = self.get_operation(data.get(CustomAttributes.RESOURCE_TYPE))  # type:ignore[arg-type]
        # A None indicate for UNKNOWN result - the vertex shouldn't be added to the passed or the failed vertices
        if result is None:
            unknown_vertices.append(data)
        elif result:
            passed_vartices.append(data)
        else:
            failed_vertices.append(data)
