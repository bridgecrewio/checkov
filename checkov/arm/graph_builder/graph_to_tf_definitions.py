from __future__ import annotations

import os
from pathlib import Path
from typing import Any, TYPE_CHECKING, cast

from checkov.arm.graph_builder.graph_components.block_types import BlockType
from checkov.arm.graph_builder.graph_components.blocks import ArmBlock

if TYPE_CHECKING:
    from checkov.common.graph.graph_builder.local_graph import _Block

def convert_graph_vertices_to_tf_definitions(
    vertices: list[ArmBlock], root_folder: str | Path | None
) -> tuple[dict[Path, Any], dict[str, dict[str, Any]]]:
    return
    # tf_definitions: dict[Path, BicepJson] = {}
    # breadcrumbs: dict[str, dict[str, Any]] = {}
    # for vertex in vertices:
    #     block_path = Path(vertex.path)
    #     # in theory block_type could be any string, but not in a Bicep Graph
    #     block_type = cast("BlockTypeAlias", vertex.block_type)
    #     bicep_element: BicepElementsAlias = BLOCK_TYPE_TO_BICEP_ELEMENTS_MAP[block_type].value
    #     element_name = vertex.name
    #
    #     if block_type == BlockType.TARGET_SCOPE:
    #         element_name = "scope"
    #
    #     tf_definitions.setdefault(block_path, {}).setdefault(bicep_element, {})[element_name] = vertex.config  # type:ignore[typeddict-item]
    #
    #     if vertex.breadcrumbs:
    #         relative_block_path = f"/{os.path.relpath(block_path, root_folder)}"
    #         add_breadcrumbs(vertex, breadcrumbs, relative_block_path)
    # return tf_definitions, breadcrumbs


# def add_breadcrumbs(vertex: BicepBlock, breadcrumbs: dict[str, dict[str, Any]], relative_block_path: str) -> None:
#     breadcrumbs.setdefault(relative_block_path, {})[vertex.name] = vertex.breadcrumbs
