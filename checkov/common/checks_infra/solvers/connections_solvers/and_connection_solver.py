from __future__ import annotations

import itertools
from typing import Optional, List, Tuple, Dict, Any, TYPE_CHECKING

from checkov.common.graph.checks_infra.enums import Operators
from checkov.common.graph.checks_infra.solvers.base_solver import BaseSolver
from checkov.common.checks_infra.solvers.connections_solvers.complex_connection_solver import ComplexConnectionSolver
from checkov.common.graph.graph_builder.graph_components.attribute_names import CustomAttributes

if TYPE_CHECKING:
    from networkx import DiGraph


class AndConnectionSolver(ComplexConnectionSolver):
    operator = Operators.AND  # noqa: CCE003  # a static attribute

    def __init__(self, solvers: Optional[List[BaseSolver]], operator: str) -> None:
        super().__init__(solvers, operator)

    def get_operation(self, graph_connector: DiGraph) -> \
            Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
        if not self.vertices_under_resource_types:
            return [], [], []
        subgraph = graph_connector.subgraph(graph_connector)
        passed, failed, unknown = self.run_attribute_solvers(subgraph)
        passed_connections, failed_connections, unknown_connections = self.run_connection_solvers(subgraph)
        passed.extend(passed_connections)
        failed.extend(failed_connections)
        unknown.extend(unknown_connections)

        failed_ids = [f[CustomAttributes.ID] for f in failed]
        unknown_ids = [u[CustomAttributes.ID] for u in unknown]
        passed = [p for p in passed if p[CustomAttributes.ID] not in itertools.chain(failed_ids, unknown_ids)]
        unknown = [u for u in unknown if u[CustomAttributes.ID] not in failed_ids]
        return self.filter_results(passed, failed, unknown)

    def _get_operation(self, *args: Any, **kwargs: Any) -> None:
        pass
