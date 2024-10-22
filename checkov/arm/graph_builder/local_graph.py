from __future__ import annotations

import logging
from typing import Any, TYPE_CHECKING

from checkov.arm.graph_builder.graph_components.block_types import BlockType
from checkov.arm.graph_builder.graph_components.blocks import ArmBlock
from checkov.arm.utils import ArmElements, extract_resource_name_from_resource_id_func, extract_resource_name_from_reference_func
from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.graph.graph_builder.graph_components.edge import Edge
from checkov.common.graph.graph_builder.local_graph import LocalGraph
from checkov.common.util.consts import START_LINE, END_LINE
from checkov.common.util.data_structures_utils import pickle_deepcopy

if TYPE_CHECKING:
    from checkov.common.graph.graph_builder.local_graph import _Block


class ArmLocalGraph(LocalGraph[ArmBlock]):
    def __init__(self, definitions: dict[str, dict[str, Any]]) -> None:
        super().__init__()
        self.vertices: list[ArmBlock] = []
        self.definitions = definitions
        self.vertices_by_path_and_id: dict[tuple[str, str], int] = {}
        self.vertices_by_name: dict[str, int] = {}

    def build_graph(self, render_variables: bool = False) -> None:
        self._create_vertices()
        logging.debug(f"[ArmLocalGraph] created {len(self.vertices)} vertices")

        self._create_edges()
        logging.debug(f"[ArmLocalGraph] created {len(self.edges)} edges")

    def _create_vertices(self) -> None:
        for file_path, definition in self.definitions.items():
            self._create_parameter_vertices(file_path=file_path, parameters=definition.get(ArmElements.PARAMETERS))
            self._create_resource_vertices(file_path=file_path, resources=definition.get(ArmElements.RESOURCES))

        for i, vertex in enumerate(self.vertices):
            self.vertices_by_block_type[vertex.block_type].append(i)
            self.vertices_block_name_map[vertex.block_type][vertex.name].append(i)
            self.vertices_by_path_and_id[(vertex.path, vertex.id)] = i
            self.vertices_by_name[vertex.name] = i

            self.in_edges[i] = []
            self.out_edges[i] = []

    def _create_parameter_vertices(self, file_path: str, parameters: dict[str, dict[str, Any]] | None) -> None:
        if not parameters:
            return

        for name, config in parameters.items():
            if name in (START_LINE, END_LINE):
                continue
            if not isinstance(config, dict):
                logging.debug(f"[ArmLocalGraph] parameter {name} has wrong type {type(config)}")
                continue

            attributes = pickle_deepcopy(config)

            self.vertices.append(
                ArmBlock(
                    name=name,
                    config=config,
                    path=file_path,
                    block_type=BlockType.PARAMETER,
                    attributes=attributes,
                    id=f"{BlockType.PARAMETER}.{name}",
                )
            )

    def _create_resource_vertices(self, file_path: str, resources: list[dict[str, Any]] | None) -> None:
        if not resources:
            return

        for config in resources:
            if "type" not in config:
                # this can't be a real ARM resource without a "type" field
                return

            resource_name = config.get("name") or "unknown"
            resource_type = config["type"]

            attributes = pickle_deepcopy(config)
            attributes[CustomAttributes.RESOURCE_TYPE] = resource_type

            self.vertices.append(
                ArmBlock(
                    name=resource_name,
                    config=config,
                    path=file_path,
                    block_type=BlockType.RESOURCE,
                    attributes=attributes,
                    id=f"{resource_type}.{resource_name}"
                )
            )

    def _create_edges(self) -> None:
        # TODO: Create variable vertices edges
        # TODO: Render variables into vertices
        for origin_vertex_index, vertex in enumerate(self.vertices):
            if 'dependsOn' in vertex.attributes:
                self._create_explicit_edge(origin_vertex_index, vertex.name, vertex.attributes['dependsOn'])
            self._create_implicit_edges(origin_vertex_index, vertex.name, vertex.attributes)

    def _create_explicit_edge(self, origin_vertex_index: int, resource_name: str, deps: list[str]) -> None:
        for dep in deps:
            if 'resourceId' in dep:
                processed_dep = extract_resource_name_from_resource_id_func(dep)
            else:
                processed_dep = dep.split('/')[-1]
            # Check if the processed dependency exists in the map
            if processed_dep in self.vertices_by_name:
                self._create_edge(processed_dep, origin_vertex_index, f'{resource_name}->{processed_dep}')
            else:
                # Dependency not found
                logging.debug(f"[ArmLocalGraph] resource dependency {processed_dep} defined in {dep} for resource"
                              f" {resource_name} not found")
                continue

    def _create_edge(self, element_name: str, origin_vertex_index: int, label: str) -> None:
        dest_vertex_index = self.vertices_by_name.get(element_name)
        if origin_vertex_index == dest_vertex_index:
            return
        edge = Edge(origin_vertex_index, dest_vertex_index, label)
        self.edges.append(edge)
        self.out_edges[origin_vertex_index].append(edge)
        self.in_edges[dest_vertex_index].append(edge)

    def _create_implicit_edges(self, origin_vertex_index: int, resource_name: str, d: dict[str, Any]) -> None:
        for _, value in d.items():
            if isinstance(value, str):
                if 'reference' in value:
                    self._create_implicit_edge(origin_vertex_index, resource_name, value)

    def _create_implicit_edge(self, origin_vertex_index: int, resource_name: str, reference_string: str) -> None:
        dep_name = extract_resource_name_from_reference_func(reference_string)
        self._create_edge(dep_name, origin_vertex_index, f'{resource_name}->{dep_name}')

    def update_vertices_configs(self) -> None:
        # not used
        pass

    @staticmethod
    def update_vertex_config(
        vertex: _Block, changed_attributes: list[str] | dict[str, Any], has_dynamic_blocks: bool = False
    ) -> None:
        # not used
        pass

    def get_resources_types_in_graph(self) -> list[str]:
        # not used
        return []
