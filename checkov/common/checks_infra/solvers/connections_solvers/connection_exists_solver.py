import itertools
from typing import List, Optional, Dict, Any, Tuple

from igraph import Graph

from checkov.common.graph.checks_infra.enums import Operators
from checkov.common.checks_infra.solvers.connections_solvers.base_connection_solver import BaseConnectionSolver
from networkx import edge_dfs
from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.typing import LibraryGraph
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

    def get_operation(
        self, graph_connector: LibraryGraph
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
        passed: List[Dict[str, Any]] = []
        failed: List[Dict[str, Any]] = []
        unknown: List[Dict[str, Any]] = []
        if not self.vertices_under_resource_types or not self.vertices_under_connected_resources_types:
            failed.extend(self.vertices_under_resource_types)
            failed.extend(self.vertices_under_connected_resources_types)
            return passed, failed, unknown

        if isinstance(graph_connector, Graph):

            for root_vertex in graph_connector.vs:
                inverted = False
                origin_attributes = None
                destination_attributes_list = []
                for vertex in graph_connector.dfsiter(root_vertex.index):
                    resource_type = vertex[CustomAttributes.RESOURCE_TYPE]
                    attributes = vertex["attr"]
                    if resource_type in self.resource_types and attributes in self.vertices_under_resource_types:
                        if not origin_attributes:
                            origin_attributes = attributes
                        elif inverted:
                            destination_attributes_list.append(attributes)
                    elif resource_type in self.connected_resources_types and attributes in self.vertices_under_connected_resources_types:
                        if not origin_attributes:
                            origin_attributes = attributes
                            inverted = True
                        else:
                            destination_attributes_list.append(attributes)

                if origin_attributes and destination_attributes_list:
                    for destination_attributes in destination_attributes_list:
                        self.populate_checks_results(origin_attributes=origin_attributes,
                                                     destination_attributes=destination_attributes, passed=passed,
                                                     failed=failed, unknown=unknown)
        else:
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
                    self.populate_checks_results(origin_attributes=origin_attributes,
                                                 destination_attributes=destination_attributes, passed=passed,
                                                 failed=failed, unknown=unknown)
                    destination_attributes["connected_node"] = origin_attributes
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
                if v not in itertools.chain(passed, unknown)
            ]
        )
        return passed, failed, unknown
