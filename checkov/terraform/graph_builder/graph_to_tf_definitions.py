import os
from typing import List, Dict, Any, Tuple

from checkov.terraform.graph_builder.graph_components.block_types import BlockType
from checkov.terraform.graph_builder.graph_components.blocks import Block


def convert_graph_vertices_to_tf_definitions(
    vertices: List[Block], root_folder: str
) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, Dict[str, Any]]]:
    tf_definitions: Dict[str, Dict[str, Any]] = {}
    breadcrumbs: Dict[str, Dict[str, Any]] = {}
    for vertex in vertices:
        block_path = vertex.path
        if not os.path.isfile(block_path):
            print(f"tried to convert vertex to tf_definitions but its path doesnt exist: {vertex}")
            continue
        tf_path = block_path
        if vertex.module_dependency:
            tf_path = f"{block_path}[{vertex.module_dependency}#{vertex.module_dependency_num}]"
        block_type = vertex.block_type.value
        if block_type == BlockType.TF_VARIABLE:
            continue
        tf_definitions.setdefault(tf_path, {}).setdefault(block_type, []).append(vertex.config)
        relative_block_path = f"/{os.path.relpath(block_path, root_folder)}"
        add_breadcrumbs(vertex, breadcrumbs, relative_block_path)
    return tf_definitions, breadcrumbs


def add_breadcrumbs(vertex: Block, breadcrumbs: Dict[str, Dict[str, Any]], relative_block_path: str) -> None:
    vertex_breadcrumbs = vertex.breadcrumbs
    if vertex_breadcrumbs:
        breadcrumbs.setdefault(relative_block_path, {})[vertex.name] = vertex_breadcrumbs
