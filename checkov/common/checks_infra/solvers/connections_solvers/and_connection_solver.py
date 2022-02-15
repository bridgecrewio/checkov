from typing import Optional, List, Tuple, Dict, Any

from networkx.classes.digraph import DiGraph

from checkov.common.graph.checks_infra.enums import Operators
from checkov.common.graph.checks_infra.solvers.base_solver import BaseSolver
from checkov.common.checks_infra.solvers.connections_solvers.complex_connection_solver import ComplexConnectionSolver
from checkov.common.graph.graph_builder.graph_components.attribute_names import CustomAttributes


class AndConnectionSolver(ComplexConnectionSolver):
    operator = Operators.AND

    def __init__(self, solvers: Optional[List[BaseSolver]], operator: str) -> None:
        super().__init__(solvers, operator)

    def get_operation(self, graph_connector: DiGraph) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        if not self.vertices_under_resource_types:
            return [], []
        subgraph = graph_connector.subgraph(graph_connector)
        passed, failed = self.run_attribute_solvers(subgraph)
        failed_ids = [f[CustomAttributes.ID] for f in failed]
        passed = [p for p in passed if p[CustomAttributes.ID] not in failed_ids]

        for connection_solver in self.get_sorted_connection_solvers():
            connection_solver.set_vertices(subgraph, failed)
            passed_solver, failed_solver = connection_solver.get_operation(subgraph)
            passed.extend(passed_solver)
            failed.extend(failed_solver)
            failed_ids.extend([f[CustomAttributes.ID] for f in failed_solver])

        passed = [p for p in passed if p[CustomAttributes.ID] not in failed_ids]

        return self.filter_results(passed, failed)

    def _get_operation(self, *args: Any, **kwargs: Any) -> None:
        pass
