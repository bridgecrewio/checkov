from __future__ import annotations

import logging
from copy import deepcopy
from enum import Enum
from pathlib import Path
from typing import Any, TYPE_CHECKING

from pycep.transformer import BicepElement
from pycep.typing import (
    BicepJson,
    ResourceAttributes,
    GlobalsAttributes,
    ParameterAttributes,
    VariableAttributes,
    OutputAttributes,
    ModuleAttributes,
)
from typing_extensions import Literal

from checkov.bicep.graph_builder.graph_components.block_types import BlockType
from checkov.bicep.graph_builder.graph_components.blocks import BicepBlock
from checkov.common.graph.graph_builder.graph_components.edge import Edge
from checkov.common.graph.graph_builder.local_graph import LocalGraph

if TYPE_CHECKING:
    from checkov.common.graph.graph_builder.graph_components.blocks import Block

BICEP_ELEMENT_TO_BLOCK_TYPE_MAP: dict[str, Literal["param", "var", "resource", "module", "output"]] = {
    "modules": BlockType.MODULE,
}


class BicepElements(str, Enum):
    GLOBALS: Literal["globals"] = "globals"
    PARAMETERS: Literal["parameters"] = "parameters"
    VARIABLES: Literal["variables"] = "variables"
    RESOURCES: Literal["resources"] = "resources"
    MODULES: Literal["modules"] = "modules"
    OUTPUTS: Literal["outputs"] = "outputs"


class BicepLocalGraph(LocalGraph):
    def __init__(self, definitions: dict[Path, BicepJson]) -> None:
        super().__init__()
        self.definitions = definitions
        self.vertices_by_name: dict[str, int] = {}

    def build_graph(self, render_variables: bool) -> None:
        self._create_vertices()
        logging.info(f"[BicepLocalGraph] created {len(self.vertices)} vertices")
        self._create_edges()
        logging.info(f"[BicepLocalGraph] created {len(self.edges)} edges")

    def _create_vertices(self) -> None:
        for file_path, bicep_conf in self.definitions.items():
            self._create_global_vertices(file_path=file_path, globals_attrs=bicep_conf.get(BicepElements.GLOBALS.value))
            self._create_param_vertices(file_path=file_path, parameters=bicep_conf.get(BicepElements.PARAMETERS.value))
            self._create_var_vertices(file_path=file_path, variables=bicep_conf.get(BicepElements.VARIABLES.value))
            self._create_resource_vertices(file_path=file_path, resources=bicep_conf.get(BicepElements.RESOURCES.value))
            self._create_module_vertices(file_path=file_path, modules=bicep_conf.get(BicepElements.MODULES.value))
            self._create_output_vertices(file_path=file_path, outputs=bicep_conf.get(BicepElements.OUTPUTS.value))

        for i, vertex in enumerate(self.vertices):
            self.vertices_by_block_type[vertex.block_type].append(i)
            self.vertices_block_name_map[vertex.block_type][vertex.name].append(i)
            self.vertices_by_name[vertex.name] = i

    def _create_global_vertices(self, file_path: Path, globals_attrs: GlobalsAttributes | None) -> None:
        if not globals_attrs:
            return

        # there can only be one target scope per file
        config = deepcopy(globals_attrs["scope"])
        attributes = deepcopy(config)

        self.vertices.append(
            BicepBlock(
                name=BlockType.TARGET_SCOPE,
                config=config,  # type:ignore[arg-type]
                path=str(file_path),
                block_type=BlockType.TARGET_SCOPE,
                attributes=attributes,  # type:ignore[arg-type]
                id=BlockType.TARGET_SCOPE,
            )
        )

    def _create_param_vertices(self, file_path: Path, parameters: dict[str, ParameterAttributes] | None) -> None:
        if not parameters:
            return

        for name, conf in parameters.items():
            config = deepcopy(conf)
            attributes = deepcopy(conf)

            self.vertices.append(
                BicepBlock(
                    name=name,
                    config=config,  # type:ignore[arg-type]
                    path=str(file_path),
                    block_type=BlockType.PARAM,
                    attributes=attributes,  # type:ignore[arg-type]
                    id=f"{BlockType.PARAM}.{name}",
                )
            )

    def _create_var_vertices(self, file_path: Path, variables: dict[str, VariableAttributes] | None) -> None:
        if not variables:
            return

        for name, conf in variables.items():
            config = deepcopy(conf)
            attributes = deepcopy(conf)

            self.vertices.append(
                BicepBlock(
                    name=name,
                    config=config,  # type:ignore[arg-type]
                    path=str(file_path),
                    block_type=BlockType.VAR,
                    attributes=attributes,  # type:ignore[arg-type]
                    id=f"{BlockType.VAR}.{name}",
                )
            )

    def _create_resource_vertices(self, file_path: Path, resources: dict[str, ResourceAttributes] | None) -> None:
        if not resources:
            return

        for name, conf in resources.items():
            config = deepcopy(conf)

            attributes: dict[str, Any] = {}
            attributes["decorators"] = deepcopy(config["decorators"])
            attributes["type_"] = config["type"]
            attributes["api_version_"] = config["api_version"]
            attributes["existing_"] = config["existing"]
            attributes.update(deepcopy(config["config"]))

            attributes["resource_type"] = config["type"]
            attributes["__start_line__"] = config["__start_line__"]
            attributes["__end_line__"] = config["__end_line__"]

            self.vertices.append(
                BicepBlock(
                    name=name,
                    config=config,  # type:ignore[arg-type]
                    path=str(file_path),
                    block_type=BlockType.RESOURCE,
                    attributes=attributes,
                    id=f"{config['type']}.{name}",
                )
            )

    def _create_module_vertices(self, file_path: Path, modules: dict[str, ModuleAttributes] | None) -> None:
        if not modules:
            return

        for name, conf in modules.items():
            config = deepcopy(conf)

            attributes: dict[str, Any] = {}
            attributes["decorators"] = deepcopy(config["decorators"])
            attributes["type_"] = config["type"]
            attributes["detail_"] = config["detail"]
            attributes.update(deepcopy(config["config"]))

            attributes["resource_type"] = config["type"]
            attributes["__start_line__"] = config["__start_line__"]
            attributes["__end_line__"] = config["__end_line__"]

            self.vertices.append(
                BicepBlock(
                    name=str(name),  # this will be fixed in pycep with the next version, currently type Token
                    config=config,  # type:ignore[arg-type]
                    path=str(file_path),
                    block_type=BlockType.MODULE,
                    attributes=attributes,
                    id=f"{config['type']}.{name}",
                )
            )

    def _create_output_vertices(self, file_path: Path, outputs: dict[str, OutputAttributes] | None) -> None:
        if not outputs:
            return

        for name, conf in outputs.items():
            config = deepcopy(conf)
            attributes = deepcopy(conf)

            self.vertices.append(
                BicepBlock(
                    name=name,
                    config=config,  # type:ignore[arg-type]
                    path=str(file_path),
                    block_type=BlockType.OUTPUT,
                    attributes=attributes,  # type:ignore[arg-type]
                    id=f"{BlockType.OUTPUT}.{name}",
                )
            )

    def _create_edges(self) -> None:
        # TODO: support connections in interpolated strings
        for origin_vertex_index, vertex in enumerate(self.vertices):
            for attr_key, attr_value in vertex.attributes.items():
                if isinstance(attr_value, BicepElement):
                    self._create_edge(
                        element_name=attr_value,
                        origin_vertex_index=origin_vertex_index,
                        label=attr_key,
                    )
                if isinstance(attr_value, list):
                    for list_value in attr_value:
                        if isinstance(list_value, BicepElement):
                            self._create_edge(
                                element_name=list_value,
                                origin_vertex_index=origin_vertex_index,
                                label=attr_key,
                            )

    def _create_edge(self, element_name: str, origin_vertex_index: int, label: str) -> None:
        vertex_name = element_name
        if "." in vertex_name:
            # special case for`bicep elements, when properties are accessed
            vertex_name = vertex_name.split(".")[0]

        dest_vertex_index = self.vertices_by_name.get(vertex_name)
        if dest_vertex_index:
            if origin_vertex_index == dest_vertex_index:
                return
            edge = Edge(origin_vertex_index, dest_vertex_index, label)
            self.edges.append(edge)
            self.out_edges[origin_vertex_index].append(edge)
            self.in_edges[dest_vertex_index].append(edge)

    def update_vertices_configs(self) -> None:
        pass

    @staticmethod
    def update_vertex_config(vertex: Block, changed_attributes: list[str] | dict[str, Any]) -> None:
        pass

    def get_resources_types_in_graph(self) -> list[str]:
        pass
