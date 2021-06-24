from typing import List, Any, Dict, Callable, Tuple

from networkx import DiGraph

from checkov.common.graph.checks_infra.enums import SolverType
from checkov.common.graph.checks_infra.solvers.base_solver import BaseSolver


class BaseFilterSolver(BaseSolver):
    def __init__(self, resource_types: List[str], attribute: str, value: Any) -> None:
        super().__init__(SolverType.FILTER)
        self.resource_types = resource_types
        self.attribute = attribute
        self.value = value
        self.vertices: List[Dict[str, Any]] = []

    def get_operation(self, *args: Any, **kwargs: Any) -> bool:
        raise NotImplementedError()

    def _get_operation(self, *args: Any, **kwargs: Any) -> Callable[..., bool]:
        raise NotImplementedError()

    def run(self, graph_connector: DiGraph) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        raise NotImplementedError()
