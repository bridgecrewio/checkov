from typing import Optional, List, Tuple, Dict, Any

from networkx.classes.digraph import DiGraph
from checkov.common.graph.checks_infra.enums import Operators
from checkov.common.graph.checks_infra.solvers.base_solver import BaseSolver
from checkov.common.checks_infra.solvers.connections_solvers.base_connection_solver import BaseConnectionSolver
from checkov.common.checks_infra.solvers.connections_solvers.complex_connection_solver import ComplexConnectionSolver
from checkov.common.graph.graph_builder.graph_components.attribute_names import CustomAttributes


class OrConnectionSolver(ComplexConnectionSolver):
    operator = Operators.OR  # noqa: CCE003  # a static attribute

    def __init__(self, solvers: Optional[List[BaseSolver]], operator: str) -> None:
        super().__init__(solvers, operator)

    def get_operation(self, graph_connector: DiGraph) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:  # type:ignore[override]
        passed, failed = self.run_attribute_solvers(graph_connector)
        failed = OrConnectionSolver._filter_failed(failed, passed)
        connection_solvers = [sub_solver for sub_solver in self.solvers if isinstance(sub_solver, BaseConnectionSolver)]
        passed_connections = []
        failed_by_hash: Dict[str, Dict[str, Any]] = {}
        for connection_solver in connection_solvers:
            connection_solver.set_vertices(graph_connector, [])
            passed_solver, failed_solvers = connection_solver.get_operation(graph_connector)
            passed_connections.extend(passed_solver)
            for f in failed_solvers:
                if f[CustomAttributes.ID] not in [p[CustomAttributes.ID] for p in passed_connections]:
                    failed_by_hash.setdefault(f[CustomAttributes.HASH], {"v": f, "count": 0})
                    failed_by_hash[f[CustomAttributes.HASH]]["count"] += 1

        for data in failed_by_hash.values():
            if data["count"] == len(connection_solvers) or data["v"] not in passed_connections:
                failed.append(data["v"])

        passed.extend(passed_connections)
        failed = OrConnectionSolver._filter_failed(failed, passed)

        return self.filter_results(passed, failed)

    @staticmethod
    def _filter_failed(failed: List[Dict[str, Any]], passed: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        filterd_failed = []
        for fail in failed:
            if fail[CustomAttributes.ID] not in [p[CustomAttributes.ID] for p in passed]:
                filterd_failed.append(fail)
            elif fail[CustomAttributes.FILE_PATH] not in [p[CustomAttributes.FILE_PATH] for p in passed]:
                filterd_failed.append(fail)
        return filterd_failed
