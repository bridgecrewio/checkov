from __future__ import annotations

import os
import logging
from typing import List, Dict, Any, Tuple

from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.graph.graph_builder.deterministic import deterministic_graph_enabled, module_chain_key
from checkov.terraform.diff_files_only import diff_files_only_enabled, repository_files
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

        if not _is_repository_file(vertex.path):
            logging.debug(f'tried to convert vertex to tf_definitions but its path does not exist: {vertex}')
            continue

        tf_path = TFDefinitionKey(file_path=vertex.path)
        if vertex.source_module_object:
            tf_path = TFDefinitionKey(file_path=vertex.path, tf_source_modules=vertex.source_module_object)
        tf_definitions.setdefault(tf_path, {}).setdefault(vertex.block_type, []).append(vertex.config)
        add_breadcrumbs(vertex, breadcrumbs, f'/{os.path.relpath(vertex.path, root_folder)}')
    return tf_definitions, breadcrumbs


def _is_repository_file(path: str) -> bool:
    if diff_files_only_enabled():
        return repository_files.exists(path)
    return os.path.isfile(path)


def add_breadcrumbs(vertex: TerraformBlock, breadcrumbs: Dict[str, Dict[str, Any]], relative_block_path: str) -> None:
    vertex_breadcrumbs = vertex.breadcrumbs
    if vertex_breadcrumbs:
        vertex_key = vertex.attributes.get(CustomAttributes.TF_RESOURCE_ADDRESS, vertex.name)
        if deterministic_graph_enabled():
            # (file, address) is shared by every root module calling the same module code; keep each instance's own
            vertex_key = breadcrumbs_key(vertex_key, vertex.source_module_object)
        breadcrumbs.setdefault(relative_block_path, {})[vertex_key] = vertex_breadcrumbs


def breadcrumbs_key(address: str, source_module: Any) -> str:
    chain = module_chain_key(source_module)
    return f"{address}#{chain}" if chain else address
