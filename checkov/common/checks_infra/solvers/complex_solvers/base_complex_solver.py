from typing import List, Any, Tuple, Dict

from networkx import DiGraph

from checkov.common.graph.checks_infra.enums import SolverType
from checkov.common.graph.checks_infra.solvers.base_solver import BaseSolver


class BaseComplexSolver(BaseSolver):
    operator = ""

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
        all_vertices_resource_types = [
            data for _, data in graph_connector.nodes(data=True) if self.resource_type_pred(data, self.resource_types)
        ]
        passed_vertices = [data for data in all_vertices_resource_types if self.get_operation(data)]
        failed_vertices = [resource for resource in all_vertices_resource_types if resource not in passed_vertices]
        return passed_vertices, failed_vertices
