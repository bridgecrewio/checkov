from __future__ import annotations

import os
from pathlib import Path
from typing import Any, TYPE_CHECKING

from checkov.arm.utils import ArmElements

if TYPE_CHECKING:
    from checkov.arm.graph_builder.graph_components.blocks import ArmBlock


def convert_graph_vertices_to_definitions(vertices: list[ArmBlock], root_folder: str | Path | None)\
        -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    arm_definitions: dict[str, dict[str, Any]] = {}
    breadcrumbs: dict[str, dict[str, Any]] = {}
    for vertex in vertices:
        block_path = vertex.path
        arm_element = vertex.block_type
        element_name = vertex.name
        if arm_element == ArmElements.RESOURCES:
            arm_definitions.setdefault(block_path, {}).setdefault(arm_element, []).append(vertex.config)
        else:
            arm_definitions.setdefault(block_path, {}).setdefault(arm_element, {})[element_name] = vertex.config

        if vertex.breadcrumbs:
            relative_block_path = f"/{os.path.relpath(block_path, root_folder)}"
            add_breadcrumbs(vertex, breadcrumbs, relative_block_path)
    return arm_definitions, breadcrumbs


def add_breadcrumbs(vertex: ArmBlock, breadcrumbs: dict[str, dict[str, Any]], relative_block_path: str) -> None:
    breadcrumbs.setdefault(relative_block_path, {})[vertex.name] = vertex.breadcrumbs
