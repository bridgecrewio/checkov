from __future__ import annotations

import os
from pathlib import Path
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from checkov.serverless.graph_builder.graph_components.blocks import ServerlessBlock


def convert_graph_vertices_to_definitions(vertices: list[ServerlessBlock], root_folder: str | Path | None)\
        -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    serverless_definitions: dict[str, dict[str, Any]] = {}
    breadcrumbs: dict[str, dict[str, Any]] = {}
    for vertex in vertices:
        block_path = vertex.path
        element_name = vertex.name.split('.')[-1]
        serverless_definitions.setdefault(block_path, {}).setdefault(vertex.block_type, {})[element_name] = vertex.config

        if vertex.breadcrumbs:
            relative_block_path = f"/{os.path.relpath(block_path, root_folder)}"
            add_breadcrumbs(vertex, breadcrumbs, relative_block_path)
    return serverless_definitions, breadcrumbs


def add_breadcrumbs(vertex: ServerlessBlock, breadcrumbs: dict[str, dict[str, Any]], relative_block_path: str) -> None:
    breadcrumbs.setdefault(relative_block_path, {})[vertex.name] = vertex.breadcrumbs
