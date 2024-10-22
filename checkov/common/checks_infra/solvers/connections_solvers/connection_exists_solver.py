from __future__ import annotations

import itertools
import logging
from typing import List, Optional, Dict, Any, Tuple

from rustworkx import PyDiGraph

from checkov.common.graph.checks_infra import debug

try:
    from networkx import edge_dfs, DiGraph
except ImportError:
    logging.info("Not able to import networkx")
    edge_dfs = lambda G : []

from checkov.common.graph.checks_infra.enums import Operators
from checkov.common.checks_infra.solvers.connections_solvers.base_connection_solver import BaseConnectionSolver
from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.typing import LibraryGraph, _RustworkxGraph
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
        passed, failed, unknown = self._get_operation(graph_connector=graph_connector)

        debug.connection_block(
            resource_types=self.resource_types,
            connected_resource_types=self.connected_resources_types,
            operator=self.operator,
            passed_resources=passed,
            failed_resources=failed,
        )

        return passed, failed, unknown

    def _get_operation(
        self, graph_connector: LibraryGraph
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
        passed: List[Dict[str, Any]] = []
        failed: List[Dict[str, Any]] = []
        unknown: List[Dict[str, Any]] = []
        if not self.vertices_under_resource_types or not self.vertices_under_connected_resources_types:
            failed.extend(self.vertices_under_resource_types)
            failed.extend(self.vertices_under_connected_resources_types)
            return passed, failed, unknown

        if isinstance(graph_connector, DiGraph):
            self.get_networkx_operation(graph_connector=graph_connector, passed=passed, failed=failed, unknown=unknown)
        elif isinstance(graph_connector, PyDiGraph):
            self.get_rustworkx_operation(graph_connector=graph_connector, passed=passed, failed=failed, unknown=unknown)
        else:
            raise Exception(f"Graph type {type(graph_connector)} not supported")

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

    def get_networkx_operation(
        self,
        graph_connector: DiGraph,
        passed: list[dict[str, Any]],
        failed: list[dict[str, Any]],
        unknown: list[dict[str, Any]],
    ) -> None:
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
                self.populate_checks_results(
                    origin_attributes=origin_attributes,
                    destination_attributes=destination_attributes,
                    passed=passed,
                    failed=failed,
                    unknown=unknown,
                )
                destination_attributes["connected_node"] = origin_attributes
                continue
            if origin_attributes.get(CustomAttributes.BLOCK_TYPE) == BlockType.OUTPUT:
                print(1)
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

    def get_rustworkx_operation(
        self,
        graph_connector: _RustworkxGraph,
        passed: list[dict[str, Any]],
        failed: list[dict[str, Any]],
        unknown: list[dict[str, Any]],
    ) -> None:
        for edge in graph_connector.edge_list():
            u, v = edge
            origin_attributes = graph_connector.nodes()[u][1]
            opposite_vertices = None
            if origin_attributes in self.vertices_under_resource_types:
                opposite_vertices = self.vertices_under_connected_resources_types
            elif origin_attributes in self.vertices_under_connected_resources_types:
                opposite_vertices = self.vertices_under_resource_types
            if not opposite_vertices:
                continue

            destination_attributes = graph_connector.nodes()[v][1]
            if destination_attributes in opposite_vertices:
                self.populate_checks_results(
                    origin_attributes=origin_attributes,
                    destination_attributes=destination_attributes,
                    passed=passed,
                    failed=failed,
                    unknown=unknown,
                )
                destination_attributes["connected_node"] = origin_attributes
                continue

            destination_block_type = destination_attributes.get(CustomAttributes.BLOCK_TYPE)
            if destination_block_type == BlockType.OUTPUT:
                try:
                    output_edges = graph_connector.adj_direction(
                        v, False
                    )  # True means inbound edges and False means outbound edges
                    output_destination_index = next(iter(output_edges))
                    output_destination = graph_connector.nodes()[output_destination_index][1]
                    output_destination_type = output_destination.get(CustomAttributes.RESOURCE_TYPE)
                    if self.is_associated_edge(
                        origin_attributes.get(CustomAttributes.RESOURCE_TYPE), output_destination_type
                    ):
                        passed.extend([origin_attributes, output_destination])
                except StopIteration:
                    continue
