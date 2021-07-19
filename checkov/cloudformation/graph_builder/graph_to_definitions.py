import os
from typing import List, Dict, Any, Tuple

from checkov.cloudformation.graph_builder.graph_components.blocks import CloudformationBlock


def convert_graph_vertices_to_definitions(
    vertices: List[CloudformationBlock], root_folder: str
) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, Dict[str, Any]]]:
    definitions: Dict[str, Dict[str, Any]] = {}
    breadcrumbs: Dict[str, Dict[str, Any]] = {}
    for vertex in vertices:
        block_path = vertex.path
        block_type = vertex.block_type
        block_name = vertex.name
        definitions.setdefault(block_path, {}).setdefault(block_type, {}).setdefault(block_name, {
            'Type': vertex.attributes['resource_type'],
            'Properties': vertex.config
        })
        relative_block_path = f"/{os.path.relpath(block_path, root_folder)}"
        add_breadcrumbs(vertex, breadcrumbs, relative_block_path)
    return definitions, breadcrumbs


def add_breadcrumbs(vertex: CloudformationBlock, breadcrumbs: Dict[str, Dict[str, Any]], relative_block_path: str) -> None:
    vertex_breadcrumbs = vertex.breadcrumbs
    if vertex_breadcrumbs:
        breadcrumbs.setdefault(relative_block_path, {})[vertex.name] = vertex_breadcrumbs
