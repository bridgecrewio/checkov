import os

from checkov.graph.terraform.graph_builder.graph_components.attribute_names import CustomAttributes


def convert_graph_vertices_to_tf_definitions(vertices, root_folder):
    tf_definitions = {}
    breadcrumbs = {}
    for vertex in vertices:
        block_path = vertex.get(CustomAttributes.FILE_PATH, '')
        if not os.path.isfile(block_path):
            print(f'tried to convert vertex to tf_definitions but its path doesnt exist: {vertex}')
            continue

        block_type = vertex.get(CustomAttributes.BLOCK_TYPE, '')
        if tf_definitions.get(block_path) is None:
            tf_definitions[block_path] = {}
        if tf_definitions.get(block_path).get(block_type) is None:
            tf_definitions.get(block_path)[block_type] = []
        tf_definitions.get(block_path)[block_type].append(vertex.get(CustomAttributes.CONFIG, {}))
        relative_block_path = f"/{os.path.relpath(block_path, root_folder)}"
        add_breadcrumbs(vertex, breadcrumbs, relative_block_path)
    print(f'breadcrumbs = {breadcrumbs}')
    return tf_definitions, breadcrumbs


def add_breadcrumbs(vertex, breadcrumbs, relative_block_path):
    vertex_breadcrumbs = vertex.get(CustomAttributes.RENDERING_BREADCRUMBS)
    if vertex_breadcrumbs:
        if breadcrumbs.get(relative_block_path) is None:
            breadcrumbs[relative_block_path] = {}
        breadcrumbs[relative_block_path][vertex.get(CustomAttributes.BLOCK_NAME)] = vertex_breadcrumbs
