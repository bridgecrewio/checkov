from __future__ import annotations

from typing import List, Optional, Dict, Any, Tuple, TYPE_CHECKING

from checkov.common.graph.checks_infra.enums import Operators
from checkov.common.checks_infra.solvers.connections_solvers.connection_exists_solver import ConnectionExistsSolver

if TYPE_CHECKING:
    from checkov.common.typing import LibraryGraph


class ConnectionNotExistsSolver(ConnectionExistsSolver):
    operator = Operators.NOT_EXISTS  # noqa: CCE003  # a static attribute

    def __init__(
        self,
        resource_types: List[str],
        connected_resources_types: List[str],
        vertices_under_resource_types: Optional[List[Dict[str, Any]]] = None,
        vertices_under_connected_resources_types: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        super().__init__(
            resource_types,
            connected_resources_types,
            vertices_under_resource_types,
            vertices_under_connected_resources_types,
        )

    def get_operation(self, graph_connector: LibraryGraph) -> \
            Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
        passed, failed, unknown = super().get_operation(graph_connector)
        return failed, passed, unknown
