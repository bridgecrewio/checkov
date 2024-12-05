from __future__ import annotations

import os
from pathlib import Path
from typing import Any, TYPE_CHECKING

from checkov.serverless.utils import ServerlessElements

if TYPE_CHECKING:
    from checkov.serverless.graph_builder.graph_components.blocks import ServerlessBlock


def convert_graph_vertices_to_definitions(vertices: list[ServerlessBlock], root_folder: str | Path | None) \
        -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    serverless_definitions: dict[str, dict[str, Any]] = {}
    breadcrumbs: dict[str, dict[str, Any]] = {}
    for vertex in vertices:
        block_path = vertex.path
        element_name = vertex.name.split('.')[-1]
        # Plugins section is formatted as a list
        if vertex.block_type == ServerlessElements.PLUGINS:
            serverless_definitions.setdefault(block_path, {}).setdefault(vertex.block_type, []).append(element_name)

        # If there is a ket named 'value' in the config it means that
        # this vertex's config contains only a single string
        elif 'value' in vertex.config:
            # If the vertex is provider or service and it only contains a string the section should look like:
            # provider: <value>
            # service: <value>
            if element_name == ServerlessElements.PROVIDER or element_name == ServerlessElements.SERVICE:
                serverless_definitions.setdefault(block_path, {})[vertex.block_type] = vertex.config['value']

            # Otherwise it's a vertex of a specific nested attribute and need to include the full path
            # Examples:
            # provider:
            #   runtime: nodejs20.x
            # custom:
            #   myCustomVar: value
            else:
                serverless_definitions.setdefault(block_path, {}).setdefault(vertex.block_type, {})[element_name] = \
                    vertex.config['value']

        # Otherwise, the vertex config is a dict
        else:
            serverless_definitions.setdefault(block_path, {}).setdefault(vertex.block_type, {})[
                element_name] = vertex.config

        if vertex.breadcrumbs:
            relative_block_path = f"/{os.path.relpath(block_path, root_folder)}"
            add_breadcrumbs(vertex, breadcrumbs, relative_block_path)
    return serverless_definitions, breadcrumbs


def add_breadcrumbs(vertex: ServerlessBlock, breadcrumbs: dict[str, dict[str, Any]], relative_block_path: str) -> None:
    breadcrumbs.setdefault(relative_block_path, {})[vertex.name] = vertex.breadcrumbs
