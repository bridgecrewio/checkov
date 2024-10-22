from __future__ import annotations

import logging
import re
from typing import Any, TYPE_CHECKING

from checkov.arm.graph_builder.graph_components.block_types import BlockType
from checkov.arm.graph_builder.graph_components.blocks import ArmBlock
from checkov.arm.graph_builder.variable_rendering.renderer import ArmVariableRenderer
from checkov.arm.utils import ArmElements
from checkov.common.graph.graph_builder import CustomAttributes, Edge
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
        # if render_variables:
        renderer = ArmVariableRenderer(self)
        renderer.render_variables_from_local_graph()

    def _create_vertices(self) -> None:
        for file_path, definition in self.definitions.items():
            self._create_parameter_vertices(file_path=file_path, parameters=definition.get(ArmElements.PARAMETERS))
            self._create_resource_vertices(file_path=file_path, resources=definition.get(ArmElements.RESOURCES))
            self._create_variables_vertices(file_path=file_path, variables=definition.get(ArmElements.VARIABLES))

        for i, vertex in enumerate(self.vertices):
            self.vertices_by_block_type[vertex.block_type].append(i)
            self.vertices_block_name_map[vertex.block_type][vertex.name].append(i)
            self.vertices_by_path_and_id[(vertex.path, vertex.id)] = i
            self.vertices_by_name[vertex.name] = i

            self.in_edges[i] = []
            self.out_edges[i] = []

    def _create_variables_vertices(self, file_path: str, variables: dict[str, dict[str, Any]] | None) -> None:
        if not variables:
            return

        for name, conf in variables.items():
            if name in ['__startline__', '__endline__']:
                continue
            if not isinstance(conf, dict):
                full_conf = {"value": pickle_deepcopy(conf)}
            else: full_conf= conf
            config = pickle_deepcopy(full_conf)
            attributes = pickle_deepcopy(full_conf)

            self.vertices.append(
                ArmBlock(
                    name=name,
                    config=config,
                    path=file_path,
                    block_type=BlockType.VARIABLE,
                    attributes=attributes,
                    id=f"{BlockType.VARIABLE}.{name}",
                )
            )


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
                    id=f"{resource_type}.{resource_name}",
                )
            )

    def _create_edges(self) -> None:
        self._create_vars_and_parameters_edges()
        #todo add explicit references edges

    def _create_edge(self, element_name: str, origin_vertex_index: int, label: str) -> None:
        vertex_name = element_name
        if "." in vertex_name:
            # special case for`bicep elements, when properties are accessed
            vertex_name = vertex_name.split(".")[0]

        dest_vertex_index = self.vertices_by_name.get(vertex_name)
        if dest_vertex_index or dest_vertex_index == 0:
            if origin_vertex_index == dest_vertex_index:
                return
            edge = Edge(origin_vertex_index, dest_vertex_index, label)
            self.edges.append(edge)
            self.out_edges[origin_vertex_index].append(edge)
            self.in_edges[dest_vertex_index].append(edge)

    def _create_vars_and_parameters_edges(self) -> None:
        pattern = r"(variables|parameters)\('(\w+)'\)"
        for origin_vertex_index, vertex in enumerate(self.vertices):
            for attr_key, attr_value in vertex.attributes.items():
                if not isinstance(attr_value, str):
                    continue
                if ArmElements.VARIABLES in attr_value or ArmElements.PARAMETERS in attr_value:
                    matches = re.findall(pattern, attr_value)
                    for match in matches:
                        var_name = match[1]
                        self._create_edge(var_name, origin_vertex_index, attr_key)

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
