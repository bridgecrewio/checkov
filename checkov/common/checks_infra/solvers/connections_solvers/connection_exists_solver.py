from __future__ import annotations

import itertools
import logging
import os
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

        # Value-based fallback for cross-module references where graph edges
        # are not created (e.g. resources linked through module outputs/variables)
        self._value_based_fallback(passed, failed, graph_connector)

        return passed, failed, unknown

    def _set_connected_node(self, source: Any, target: Any) -> None:
        source.setdefault(CustomAttributes.CONNECTED_NODE, {})[tuple(self.connected_resources_types)] = target

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
                self._set_connected_node(destination_attributes, origin_attributes)
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
                self._set_connected_node(destination_attributes, origin_attributes)
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

    @staticmethod
    def _module_scope(vertex: dict[str, Any]) -> tuple[str, bool]:
        """Return (project root directory, is inside a module) for a vertex.

        Resources inside a module carry a source module object whose path is the
        file containing the module call; ``nested_tf_module`` points to the parent
        call.  The project root is the directory of the outermost call.  Root-level
        resources have no source module object, so their own directory is the root.
        """
        module = vertex.get(CustomAttributes.SOURCE_MODULE_OBJECT)
        if not module:
            return os.path.dirname(vertex.get(CustomAttributes.FILE_PATH) or ""), False
        while True:
            parent = module.get("nested_tf_module") if isinstance(module, dict) else module.nested_tf_module
            if not parent:
                break
            module = parent
        path = module.get("path") if isinstance(module, dict) else module.path
        return os.path.dirname(path or ""), True

    def _value_based_fallback(
        self,
        passed: list[dict[str, Any]],
        failed: list[dict[str, Any]],
        graph_connector: DiGraph | Any,
    ) -> None:
        """Move origin resources from failed to passed when a connected resource
        references them by rendered attribute value across a module boundary.

        This handles references between sibling modules (e.g. a value passed from
        one module's output into another module's variable), where no graph edge
        is created.  A match requires all of the following:
          * at least one of the two resources is inside a module,
          * both resources belong to the same project (same root module directory),
          * the resources are defined in different files,
          * the origin name is resolved and unique among origin resources of
            that project (ambiguous names are left to the edge-based result).
        """
        if not self.vertices_under_resource_types or not self.vertices_under_connected_resources_types:
            return

        unresolved_prefixes = ("var.", "module.", "local.")

        def resolved_name(vertex: dict[str, Any]) -> str | None:
            name = vertex.get("name")
            if not isinstance(name, str) or not name or name.startswith(unresolved_prefixes):
                return None
            return name

        # (project root, name) -> number of origin resources using that name
        name_counts: dict[tuple[str, str], int] = {}
        for vertex in self.vertices_under_resource_types:
            name = resolved_name(vertex)
            if name:
                key = (self._module_scope(vertex)[0], name)
                name_counts[key] = name_counts.get(key, 0) + 1

        # (project root, string value) -> [(file path, inside module)] of connected resources
        connected_type_set = set(self.connected_resources_types)
        connected_values: dict[tuple[str, str], list[tuple[str, bool]]] = {}
        if isinstance(graph_connector, PyDiGraph):
            nodes = (n[1] for n in graph_connector.nodes())
        else:
            nodes = (data for _, data in graph_connector.nodes(data=True))
        for node in nodes:
            if node.get(CustomAttributes.RESOURCE_TYPE) not in connected_type_set:
                continue
            root, in_module = self._module_scope(node)
            entry = (node.get(CustomAttributes.FILE_PATH, ""), in_module)
            for val in {v for v in node.values() if isinstance(v, str)}:
                connected_values.setdefault((root, val), []).append(entry)

        to_pass: list[dict[str, Any]] = []
        for vertex in failed:
            if vertex.get(CustomAttributes.RESOURCE_TYPE) not in self.resource_types:
                continue
            name = resolved_name(vertex)
            if not name:
                continue
            root, origin_in_module = self._module_scope(vertex)
            if name_counts.get((root, name), 0) != 1:
                continue  # ambiguous name within the project
            origin_file = vertex.get(CustomAttributes.FILE_PATH, "")
            for file_path, connected_in_module in connected_values.get((root, name), ()):
                # same file: the edge-based check is authoritative;
                # both root-level: no module boundary, edges would exist
                if file_path != origin_file and (origin_in_module or connected_in_module):
                    to_pass.append(vertex)
                    break

        for vertex in to_pass:
            failed.remove(vertex)
            if vertex not in passed:
                passed.append(vertex)
