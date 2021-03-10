import logging
import os

from checkov.graph.terraform.graph_builder.graph_components.blocks import Block


def convert_graph_vertices_to_tf_definitions(vertices, root_folder):
    tf_definitions = {}
    breadcrumbs = {}
    for vertex in vertices:
        block_path = vertex.path
        if not os.path.isfile(block_path):
            print(f'tried to convert vertex to tf_definitions but its path doesnt exist: {vertex}')
            continue

        block_type = vertex.block_type.value
        if tf_definitions.get(block_path) is None:
            tf_definitions[block_path] = {}
        if tf_definitions.get(block_path).get(block_type) is None:
            tf_definitions.get(block_path)[block_type] = []
        tf_definitions.get(block_path)[block_type].append(vertex.config)
        relative_block_path = f"/{os.path.relpath(block_path, root_folder)}"
        add_breadcrumbs(vertex, breadcrumbs, relative_block_path)
    logging.info(f'breadcrumbs = {breadcrumbs}')
    return tf_definitions, breadcrumbs


def add_breadcrumbs(vertex: Block, breadcrumbs, relative_block_path):
    vertex_breadcrumbs = vertex.breadcrumbs
    if vertex_breadcrumbs:
        if breadcrumbs.get(relative_block_path) is None:
            breadcrumbs[relative_block_path] = {}
        breadcrumbs[relative_block_path][vertex.name] = vertex_breadcrumbs
