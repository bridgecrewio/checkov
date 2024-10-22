from __future__ import annotations

import itertools
from typing import Optional, List, Tuple, Dict, Any, TYPE_CHECKING

from checkov.common.checks_infra.solvers.connections_solvers.base_connection_solver import BaseConnectionSolver
from checkov.common.graph.checks_infra.enums import Operators
from checkov.common.graph.checks_infra.solvers.base_solver import BaseSolver
from checkov.common.checks_infra.solvers.connections_solvers.complex_connection_solver import ComplexConnectionSolver

if TYPE_CHECKING:
    from checkov.common.typing import LibraryGraph


class OrConnectionSolver(ComplexConnectionSolver):
    operator = Operators.OR  # noqa: CCE003  # a static attribute

    def __init__(self, solvers: Optional[List[BaseSolver]], operator: str) -> None:
        super().__init__(solvers, operator)

    def get_operation(self, graph_connector: LibraryGraph) -> \
            Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
        passed, failed, unknown = self.run_attribute_solvers(graph_connector)
        connection_solvers = [sub_solver for sub_solver in self.solvers if isinstance(sub_solver, BaseConnectionSolver)]
        for connection_solver in connection_solvers:
            connection_solver.set_vertices(graph_connector, [], [])
            passed_solver, failed_solver, unknown_solver = connection_solver.get_operation(graph_connector)
            passed.extend(passed_solver)
            failed.extend(failed_solver)
            unknown.extend(unknown_solver)

        passed_path_and_ids = [(ComplexConnectionSolver.get_check_identifier(p)) for p in passed]
        unknown_path_and_ids = [(ComplexConnectionSolver.get_check_identifier(u)) for u in unknown]
        unknown = [u for u in unknown if (ComplexConnectionSolver.get_check_identifier(u)) not in passed_path_and_ids]
        failed = [f for f in failed if (ComplexConnectionSolver.get_check_identifier(f)) not in itertools.chain(passed_path_and_ids, unknown_path_and_ids)]
        return self.filter_results(passed, failed, unknown)
