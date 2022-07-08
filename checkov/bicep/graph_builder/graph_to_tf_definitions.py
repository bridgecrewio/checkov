from __future__ import annotations

import os
from pathlib import Path
from typing import Any, TYPE_CHECKING, cast

from pycep.typing import BicepJson

from checkov.bicep.graph_builder.graph_components.block_types import BlockType, BlockTypeAlias
from checkov.bicep.graph_builder.local_graph import BicepElements, BicepElementsAlias

if TYPE_CHECKING:
    from checkov.bicep.graph_builder.graph_components.blocks import BicepBlock

BLOCK_TYPE_TO_BICEP_ELEMENTS_MAP: dict[BlockTypeAlias, BicepElements] = {
    BlockType.MODULE: BicepElements.MODULES,
    BlockType.OUTPUT: BicepElements.OUTPUTS,
    BlockType.PARAM: BicepElements.PARAMETERS,
    BlockType.RESOURCE: BicepElements.RESOURCES,
    BlockType.TARGET_SCOPE: BicepElements.GLOBALS,
    BlockType.VAR: BicepElements.VARIABLES,
}


def convert_graph_vertices_to_tf_definitions(
    vertices: list[BicepBlock], root_folder: str | Path | None
) -> tuple[dict[Path, BicepJson], dict[str, dict[str, Any]]]:
    tf_definitions: dict[Path, BicepJson] = {}
    breadcrumbs: dict[str, dict[str, Any]] = {}
    for vertex in vertices:
        block_path = Path(vertex.path)
        # in theory block_type could be any string, but not in a Bicep Graph
        block_type = cast(BlockTypeAlias, vertex.block_type)
        bicep_element: BicepElementsAlias = BLOCK_TYPE_TO_BICEP_ELEMENTS_MAP[block_type].value
        element_name = vertex.name

        if block_type == BlockType.TARGET_SCOPE:
            element_name = "scope"

        tf_definitions.setdefault(block_path, {}).setdefault(bicep_element, {})[element_name] = vertex.config  # type:ignore[typeddict-item]

        if vertex.breadcrumbs:
            relative_block_path = f"/{os.path.relpath(block_path, root_folder)}"
            add_breadcrumbs(vertex, breadcrumbs, relative_block_path)
    return tf_definitions, breadcrumbs


def add_breadcrumbs(vertex: BicepBlock, breadcrumbs: dict[str, dict[str, Any]], relative_block_path: str) -> None:
    breadcrumbs.setdefault(relative_block_path, {})[vertex.name] = vertex.breadcrumbs
