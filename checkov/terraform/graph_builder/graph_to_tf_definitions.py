from __future__ import annotations

import os
from typing import List, Dict, Any, Tuple

from checkov.common.graph.graph_builder import CustomAttributes
from checkov.terraform.modules.module_objects import TFDefinitionKey
from checkov.terraform.graph_builder.graph_components.block_types import BlockType
from checkov.terraform.graph_builder.graph_components.blocks import TerraformBlock


def convert_graph_vertices_to_tf_definitions(
    vertices: List[TerraformBlock], root_folder: str
) -> Tuple[Dict[TFDefinitionKey, Dict[str, Any]], Dict[str, Dict[str, Any]]]:
    tf_definitions: Dict[TFDefinitionKey, Dict[str, Any]] = {}
    breadcrumbs: Dict[str, Dict[str, Any]] = {}
    for vertex in vertices:
        block_path = vertex.path
        if not os.path.isfile(block_path):
            print(f"tried to convert vertex to tf_definitions but its path doesnt exist: {vertex}")
            continue
        block_type = vertex.block_type
        if block_type == BlockType.TF_VARIABLE:
            continue

        tf_path = TFDefinitionKey(file_path=block_path)
        if vertex.source_module_object:
            tf_path = TFDefinitionKey(file_path=block_path, tf_source_modules=vertex.source_module_object)
        tf_definitions.setdefault(tf_path, {}).setdefault(block_type, []).append(vertex.config)
        relative_block_path = f"/{os.path.relpath(block_path, root_folder)}"
        add_breadcrumbs(vertex, breadcrumbs, relative_block_path)
    return tf_definitions, breadcrumbs


def add_breadcrumbs(vertex: TerraformBlock, breadcrumbs: Dict[str, Dict[str, Any]], relative_block_path: str) -> None:
    vertex_breadcrumbs = vertex.breadcrumbs
    if vertex_breadcrumbs:
        vertex_key = vertex.attributes.get(CustomAttributes.TF_RESOURCE_ADDRESS, vertex.name)
        breadcrumbs.setdefault(relative_block_path, {})[vertex_key] = vertex_breadcrumbs
