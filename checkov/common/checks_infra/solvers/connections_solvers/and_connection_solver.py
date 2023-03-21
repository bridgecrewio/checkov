from __future__ import annotations

import itertools
from typing import Optional, List, Tuple, Dict, Any, TYPE_CHECKING

from checkov.common.graph.checks_infra.enums import Operators
from checkov.common.graph.checks_infra.solvers.base_solver import BaseSolver
from checkov.common.checks_infra.solvers.connections_solvers.complex_connection_solver import ComplexConnectionSolver

if TYPE_CHECKING:
    from checkov.common.typing import LibraryGraph


class AndConnectionSolver(ComplexConnectionSolver):
    operator = Operators.AND  # noqa: CCE003  # a static attribute

    def __init__(self, solvers: Optional[List[BaseSolver]], operator: str) -> None:
        super().__init__(solvers, operator)

    def get_operation(self, graph_connector: LibraryGraph) -> \
            Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
        if not self.vertices_under_resource_types:
            return [], [], []

        passed, failed, unknown = self.run_attribute_solvers(graph_connector)
        failed_or_unknown_ids = [(ComplexConnectionSolver.get_check_identifier(f)) for f in itertools.chain(failed, unknown)]
        passed = [p for p in passed if (ComplexConnectionSolver.get_check_identifier(p)) not in failed_or_unknown_ids]

        for connection_solver in self.get_sorted_connection_solvers():
            connection_solver.set_vertices(graph_connector, failed, unknown)
            passed_solver, failed_solver, unknown_solver = connection_solver.get_operation(graph_connector)
            passed.extend(passed_solver)
            failed.extend(failed_solver)
            unknown.extend(unknown_solver)
            failed_or_unknown_ids.extend((ComplexConnectionSolver.get_check_identifier(f)) for f in itertools.chain(failed_solver, unknown_solver))

        failed_ids = [(ComplexConnectionSolver.get_check_identifier(f)) for f in failed]
        unknown_ids = [(ComplexConnectionSolver.get_check_identifier(u)) for u in unknown]
        passed = [p for p in passed if (ComplexConnectionSolver.get_check_identifier(p)) not in itertools.chain(failed_ids, unknown_ids)]
        unknown = [u for u in unknown if (ComplexConnectionSolver.get_check_identifier(u)) not in failed_ids]
        return self.filter_results(passed, failed, unknown)

    def _get_operation(self, *args: Any, **kwargs: Any) -> None:
        pass
