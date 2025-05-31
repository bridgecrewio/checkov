from __future__ import annotations

import os
import logging
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
        if vertex.block_type == BlockType.TF_VARIABLE:
            continue

        if not os.path.isfile(vertex.path):
            logging.debug(f'tried to convert vertex to tf_definitions but its path does not exist: {vertex}')
            continue

        tf_path = TFDefinitionKey(file_path=vertex.path)
        if vertex.source_module_object:
            tf_path = TFDefinitionKey(file_path=vertex.path, tf_source_modules=vertex.source_module_object)
        tf_definitions.setdefault(tf_path, {}).setdefault(vertex.block_type, []).append(vertex.config)
        add_breadcrumbs(vertex, breadcrumbs, f'/{os.path.relpath(vertex.path, root_folder)}')
    return tf_definitions, breadcrumbs


def add_breadcrumbs(vertex: TerraformBlock, breadcrumbs: Dict[str, Dict[str, Any]], relative_block_path: str) -> None:
    vertex_breadcrumbs = vertex.breadcrumbs
    if vertex_breadcrumbs:
        vertex_key = vertex.attributes.get(CustomAttributes.TF_RESOURCE_ADDRESS, vertex.name)
        breadcrumbs.setdefault(relative_block_path, {})[vertex_key] = vertex_breadcrumbs
