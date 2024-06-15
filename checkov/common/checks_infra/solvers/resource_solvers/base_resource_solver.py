from __future__ import annotations

from abc import abstractmethod
from typing import Any, Callable, TYPE_CHECKING

from networkx import DiGraph

from checkov.common.graph.checks_infra.enums import SolverType
from checkov.common.graph.checks_infra.solvers.base_solver import BaseSolver
from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.graph.graph_builder.graph_components.block_types import BlockType

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
        passed_vertices: list[dict[str, Any]] = []
        failed_vertices: list[dict[str, Any]] = []

        if isinstance(graph_connector, DiGraph):
            select_kwargs = {"block_type__eq": BlockType.RESOURCE}

            for data in graph_connector.vs.select(**select_kwargs)["attr"]:
                result = self.get_operation(resource_type=data.get(CustomAttributes.RESOURCE_TYPE))
                if result:
                    passed_vertices.append(data)
                else:
                    failed_vertices.append(data)

            return passed_vertices, failed_vertices, []

        for _, data in graph_connector.nodes(data=True):
            result = self.get_operation(resource_type=data.get(CustomAttributes.RESOURCE_TYPE))
            if result:
                passed_vertices.append(data)
            else:
                failed_vertices.append(data)

        return passed_vertices, failed_vertices, []
