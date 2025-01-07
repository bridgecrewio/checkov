from pathlib import Path

from checkov.common.graph.db_connectors.rustworkx.rustworkx_db_connector import RustworkxConnector
from checkov.common.util.consts import LINE_FIELD_NAMES
from checkov.serverless.graph_builder.graph_to_definitions import convert_graph_vertices_to_definitions
from checkov.serverless.graph_manager import ServerlessGraphManager
from checkov.serverless.utils import get_files_definitions, ServerlessElements

RESOURCES_DIR = Path(__file__).parent / 'resources'

def test_graph_from_file_def_and_graph_def():
    # compare graph created from definition created by file and graph created by definition created from graph
    # given
    test_file = RESOURCES_DIR / "serverless.yaml"
    definitions_from_file, _ = get_files_definitions([str(test_file)])
    graph_manager = ServerlessGraphManager(db_connector=RustworkxConnector())

    local_graph = graph_manager.build_graph_from_definitions(definitions=definitions_from_file, render_variables=False)

    definition_from_graph, _ = convert_graph_vertices_to_definitions(
        vertices=local_graph.vertices,
        root_folder=test_file,
    )
    local_graph_from_new_def = graph_manager.build_graph_from_definitions(definitions=definition_from_graph,
                                                                          render_variables=False)

    # then
    assert len(local_graph.vertices) == len(local_graph_from_new_def.vertices)
    assert len(local_graph.edges) == len(local_graph_from_new_def.edges)

    assert len(local_graph.vertices) == len(local_graph_from_new_def.vertices)
    assert len(local_graph.edges) == len(local_graph_from_new_def.edges)
    assert len(local_graph.vertices_by_block_type[ServerlessElements.PARAMS]) == len(
        local_graph_from_new_def.vertices_by_block_type[ServerlessElements.PARAMS])
    assert len(local_graph.vertices_by_block_type[ServerlessElements.FUNCTIONS]) == len(
        local_graph_from_new_def.vertices_by_block_type[ServerlessElements.FUNCTIONS])
    assert len(local_graph.vertices_by_block_type[ServerlessElements.PROVIDER]) == len(
        local_graph_from_new_def.vertices_by_block_type[ServerlessElements.PROVIDER])
    assert len(local_graph.vertices_by_block_type[ServerlessElements.LAYERS]) == len(
        local_graph_from_new_def.vertices_by_block_type[ServerlessElements.LAYERS])
    assert len(local_graph.vertices_by_block_type[ServerlessElements.CUSTOM]) == len(
        local_graph_from_new_def.vertices_by_block_type[ServerlessElements.CUSTOM])
    assert len(local_graph.vertices_by_block_type[ServerlessElements.PACKAGE]) == len(
        local_graph_from_new_def.vertices_by_block_type[ServerlessElements.PACKAGE])
    assert len(local_graph.vertices_by_block_type[ServerlessElements.PLUGINS]) == len(
        local_graph_from_new_def.vertices_by_block_type[ServerlessElements.PLUGINS])
    assert len(local_graph.vertices_by_block_type[ServerlessElements.SERVICE]) == len(
        local_graph_from_new_def.vertices_by_block_type[ServerlessElements.SERVICE])

    for vertex in local_graph.vertices:
        vertex_file = vertex.path
        vertex_name = vertex.name

        matching_vertex_index = local_graph_from_new_def.vertices_by_path_and_name[(vertex_file, vertex_name)]
        matching_vertex = local_graph_from_new_def.vertices[matching_vertex_index]
        for attribute, value in matching_vertex.config.items():
            assert isinstance(vertex.config[attribute], type(value))
            assert value == vertex.config[attribute]
