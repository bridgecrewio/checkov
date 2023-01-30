from __future__ import annotations

from typing import List, Optional, Dict, Any, Tuple, TYPE_CHECKING
from checkov.common.checks_infra.solvers import ConnectionExistsSolver
from checkov.common.graph.checks_infra.enums import Operators

if TYPE_CHECKING:
    from checkov.common.typing import LibraryGraph


class ConnectionOneExistsSolver(ConnectionExistsSolver):
    operator = Operators.ONE_EXISTS  # noqa: CCE003  # a static attribute

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
        failed = [f for f in failed if f not in passed]
        unknown = [u for u in unknown if u not in passed]
        return passed, failed, unknown
