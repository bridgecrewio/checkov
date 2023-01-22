from __future__ import annotations

import logging
from copy import deepcopy
from typing import TYPE_CHECKING, Any

from checkov.bicep.graph_builder.graph_components.block_types import BlockType
from checkov.common.graph.graph_builder import Edge, CustomAttributes
from checkov.common.graph.graph_builder.consts import GraphSource
from checkov.common.graph.graph_builder.graph_components.blocks import Block
from checkov.common.graph.graph_builder.local_graph import LocalGraph
from checkov.common.util.consts import START_LINE, END_LINE
from checkov.dockerfile.graph_builder.graph_components.resource_types import ResourceType
from checkov.dockerfile.utils import DOCKERFILE_STARTLINE, DOCKERFILE_ENDLINE

if TYPE_CHECKING:
    from dockerfile_parse.parser import _Instruction  # only in extra_stubs
    from checkov.common.graph.graph_builder.local_graph import _Block


class DockerfileLocalGraph(LocalGraph[Block]):
    def __init__(self, definitions: dict[str, dict[str, list[_Instruction]]]) -> None:
        super().__init__()
        self.vertices: list[Block] = []
        self.definitions = definitions
        self.vertices_by_path_and_name: dict[tuple[str, str], int] = {}

    def build_graph(self, render_variables: bool = False) -> None:
        self._create_vertices()
        logging.debug(f"[DockerfileLocalGraph] created {len(self.vertices)} vertices")

        for i, vertex in enumerate(self.vertices):
            self.vertices_by_block_type[vertex.block_type].append(i)
            self.vertices_block_name_map[vertex.block_type][vertex.name].append(i)
            self.vertices_by_path_and_name[(vertex.path, vertex.name)] = i

            self.in_edges[i] = []
            self.out_edges[i] = []

        self._create_edges()
        logging.debug(f"[DockerfileLocalGraph] created {len(self.edges)} edges")

    def _create_vertices(self) -> None:
        for file_path, definition in self.definitions.items():
            for instruction_type, instructions in definition.items():
                self._create_instruction_vertices(
                    file_path=file_path,
                    instruction_type=instruction_type,
                    instructions=instructions,
                )

    def _create_instruction_vertices(
        self, file_path: str, instruction_type: str, instructions: list[_Instruction]
    ) -> None:
        """Creates supported 'instruction_type' vertices"""

        if instruction_type == "COMMENT":
            # not interested in comments
            return

        for instruction in instructions:
            resource_type = ResourceType.__dict__.get(instruction_type)
            if not resource_type:
                logging.warning(f"An unsupported instruction {instruction_type} was used in {file_path}")
                continue

            config = {
                "content": instruction["content"],
                "value": instruction["value"],
                START_LINE: instruction[DOCKERFILE_STARTLINE],
                END_LINE: instruction[DOCKERFILE_ENDLINE],
            }

            attributes = deepcopy(config)
            attributes[CustomAttributes.RESOURCE_TYPE] = resource_type

            self.vertices.append(
                Block(
                    name=resource_type,
                    config=config,
                    path=file_path,
                    block_type=BlockType.RESOURCE,
                    attributes=attributes,
                    id=resource_type,
                    source=GraphSource.DOCKERFILE,
                )
            )

    def _create_edges(self) -> None:
        pass

    def _create_edge(self, origin_vertex_index: int, dest_vertex_index: int, label: str = "default") -> None:
        if origin_vertex_index == dest_vertex_index:
            # this should not happen
            return

        edge = Edge(origin_vertex_index, dest_vertex_index, label)
        self.edges.append(edge)
        self.out_edges[origin_vertex_index].append(edge)
        self.in_edges[dest_vertex_index].append(edge)

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
