import itertools
from typing import List, Optional, Dict, Any, Tuple

from checkov.common.graph.checks_infra.enums import Operators
from checkov.common.checks_infra.solvers.connections_solvers.base_connection_solver import BaseConnectionSolver
from networkx import edge_dfs, DiGraph
from checkov.common.graph.graph_builder import CustomAttributes
from checkov.terraform.graph_builder.graph_components.block_types import BlockType


class ConnectionExistsSolver(BaseConnectionSolver):
    operator = Operators.EXISTS  # noqa: CCE003  # a static attribute

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

    def get_operation(self, graph_connector: DiGraph) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:  # type:ignore[override]
        passed = []
        failed = []
        for u, v in edge_dfs(graph_connector):
            origin_attributes = graph_connector.nodes(data=True)[u]
            opposite_vertices = None
            if origin_attributes in self.vertices_under_resource_types:
                opposite_vertices = self.vertices_under_connected_resources_types
            elif origin_attributes in self.vertices_under_connected_resources_types:
                opposite_vertices = self.vertices_under_resource_types
            if not opposite_vertices:
                continue

            destination_attributes = graph_connector.nodes(data=True)[v]
            if destination_attributes in opposite_vertices:
                if origin_attributes in self.excluded_vertices or destination_attributes in self.excluded_vertices:
                    failed.extend([origin_attributes, destination_attributes])
                else:
                    passed.extend([origin_attributes, destination_attributes])
                destination_attributes['connected_node'] = origin_attributes
                continue

            destination_block_type = destination_attributes.get(CustomAttributes.BLOCK_TYPE)
            if destination_block_type == BlockType.OUTPUT:
                try:
                    output_edges = graph_connector.edges(v, data=True)
                    _, output_destination, _ = next(iter(output_edges))
                    output_destination = graph_connector.nodes(data=True)[output_destination]
                    output_destination_type = output_destination.get(CustomAttributes.RESOURCE_TYPE)
                    if self.is_associated_edge(
                        origin_attributes.get(CustomAttributes.RESOURCE_TYPE), output_destination_type
                    ):
                        passed.extend([origin_attributes, output_destination])
                except StopIteration:
                    continue
        failed.extend(
            [
                v
                for v in itertools.chain(
                    self.vertices_under_resource_types, self.vertices_under_connected_resources_types
                )
                if v not in passed
            ]
        )
        return passed, failed
