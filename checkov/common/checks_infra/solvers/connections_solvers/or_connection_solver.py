from __future__ import annotations

import itertools
from typing import Optional, List, Tuple, Dict, Any, TYPE_CHECKING

from checkov.common.graph.checks_infra.enums import Operators
from checkov.common.graph.checks_infra.solvers.base_solver import BaseSolver
from checkov.common.checks_infra.solvers.connections_solvers.complex_connection_solver import ComplexConnectionSolver
from checkov.common.graph.graph_builder.graph_components.attribute_names import CustomAttributes

if TYPE_CHECKING:
    from networkx import DiGraph


class OrConnectionSolver(ComplexConnectionSolver):
    operator = Operators.OR  # noqa: CCE003  # a static attribute

    def __init__(self, solvers: Optional[List[BaseSolver]], operator: str) -> None:
        super().__init__(solvers, operator)

    def get_operation(self, graph_connector: DiGraph) -> \
            Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
        passed, failed, unknown = self.run_attribute_solvers(graph_connector)
        passed_connections, failed_connections, unknown_connections = self.run_connection_solvers(graph_connector)
        passed.extend(passed_connections)
        failed.extend(failed_connections)
        unknown.extend(unknown_connections)

        passed_path_and_ids = [(p[CustomAttributes.ID], p[CustomAttributes.FILE_PATH]) for p in passed]
        unknown_path_and_ids = [(u[CustomAttributes.ID], u[CustomAttributes.FILE_PATH]) for u in unknown]
        unknown = [u for u in unknown if u[CustomAttributes.ID] not in passed_path_and_ids]
        failed = [f for f in failed if (f[CustomAttributes.ID], f[CustomAttributes.FILE_PATH]) not in
                  itertools.chain(passed_path_and_ids, unknown_path_and_ids)]
        return self.filter_results(passed, failed, unknown)
