from __future__ import annotations

from typing import List, Any, Tuple, Dict, TYPE_CHECKING

from checkov.common.graph.checks_infra.enums import SolverType
from checkov.common.graph.checks_infra.solvers.base_solver import BaseSolver

if TYPE_CHECKING:
    from networkx import DiGraph


class BaseComplexSolver(BaseSolver):
    operator = ""  # noqa: CCE003  # a static attribute

    def __init__(self, solvers: List[BaseSolver], resource_types: List[str]) -> None:
        if solvers is None:
            solvers = []
        self.solvers = solvers
        self.resource_types = resource_types
        super().__init__(SolverType.COMPLEX)

    def _get_operation(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError()

    def _get_negative_op(self, *args: Any) -> Any:
        return not self._get_operation(args)

    def run(self, graph_connector: DiGraph) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        passed_vertices = []
        failed_vertices = []
        for _, data in graph_connector.nodes(data=True):
            if self.resource_type_pred(data, self.resource_types):
                if self.get_operation(data):
                    passed_vertices.append(data)
                else:
                    failed_vertices.append(data)
        return passed_vertices, failed_vertices
