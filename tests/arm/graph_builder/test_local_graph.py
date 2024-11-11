from pathlib import Path
from unittest.mock import MagicMock

from checkov.arm.graph_builder.graph_to_definitions import convert_graph_vertices_to_definitions
from checkov.arm.graph_builder.local_graph import ArmLocalGraph, ArmBlock
from checkov.arm.graph_manager import ArmGraphManager
from checkov.arm.utils import get_files_definitions, ArmElements
from checkov.common.graph.db_connectors.rustworkx.rustworkx_db_connector import RustworkxConnector

EXAMPLES_DIR = Path(__file__).parent.parent / "examples"
EXPLICIT_DEPS_DIR = EXAMPLES_DIR / "ExplicitDepsResources"
IMPLICIT_DEPS_DIR = EXAMPLES_DIR / "ImplicitDepsResources"


def test_graph_explicit_deps():
    test_files = [str(EXPLICIT_DEPS_DIR / "subnet.json"),
                  str(EXPLICIT_DEPS_DIR / "storage.json"),
                  str(EXPLICIT_DEPS_DIR / "interface.json")]
    definitions, _, _ = get_files_definitions(test_files)
    test_graph = ArmLocalGraph(definitions)
    test_graph.build_graph()

    assert len(test_graph.vertices) == 6
    assert len(test_graph.edges) == 5

    assert len(test_graph.vertices_by_block_type[ArmElements.RESOURCES]) == 6


def test_graph_implicit_deps():
    test_files = [str(IMPLICIT_DEPS_DIR / "subnet.json"),
                  str(IMPLICIT_DEPS_DIR / "storage.json"),
                  str(IMPLICIT_DEPS_DIR / "interface.json")]
    definitions, _, _ = get_files_definitions(test_files)
    test_graph = ArmLocalGraph(definitions)
    test_graph.build_graph()

    assert len(test_graph.vertices) == 6
    assert len(test_graph.edges) == 4

    assert len(test_graph.vertices_by_block_type[ArmElements.RESOURCES]) == 6


def test_graph_params_vars():
    # given
    test_file = EXAMPLES_DIR / "container_instance.json"
    definitions, _, _ = get_files_definitions([str(test_file)])
    local_graph = ArmLocalGraph(definitions=definitions)
    # when
    local_graph.build_graph(render_variables=False)

    # then
    assert len(local_graph.vertices) == 18
    assert len(local_graph.edges) == 20

    assert len(local_graph.vertices_by_block_type[ArmElements.PARAMETERS]) == 11
    assert len(local_graph.vertices_by_block_type[ArmElements.RESOURCES]) == 4
    assert len(local_graph.vertices_by_block_type[ArmElements.VARIABLES]) == 3


def test_graph_from_file_def_and_graph_def():
    # compare graph created from definition created by file and graph created by definition created from graph
    # given
    test_file = EXAMPLES_DIR / "convert_def_test.json"
    definitions_from_file, _, _ = get_files_definitions([str(test_file)])
    graph_manager = ArmGraphManager(db_connector=RustworkxConnector())

    local_graph = graph_manager.build_graph_from_definitions(definitions=definitions_from_file, render_variables=False)

    definition_from_graph, _= convert_graph_vertices_to_definitions(
                vertices=local_graph.vertices,
                root_folder=test_file,
            )
    local_graph_from_new_def = graph_manager.build_graph_from_definitions(definitions=definition_from_graph, render_variables=False)

    # then
    assert len(local_graph.vertices) == len(local_graph_from_new_def.vertices)
    assert len(local_graph.edges) == len(local_graph_from_new_def.edges)


    assert len(local_graph.vertices_by_block_type[ArmElements.PARAMETERS]) == len(local_graph_from_new_def.vertices_by_block_type[ArmElements.PARAMETERS])
    assert len(local_graph.vertices_by_block_type[ArmElements.RESOURCES]) == len(local_graph_from_new_def.vertices_by_block_type[ArmElements.RESOURCES])
    assert len(local_graph.vertices_by_block_type[ArmElements.VARIABLES]) == len(local_graph_from_new_def.vertices_by_block_type[ArmElements.VARIABLES])

def test_update_vertices_names():
    graph = ArmLocalGraph(definitions={})

    graph.vertices = [
        ArmBlock(name="variables(name1)", config={"name": "updatedName1"}, block_type=ArmElements.RESOURCES, path='', attributes={}, id='1'),
        ArmBlock(name="name2", config={"name": "name2"}, block_type=ArmElements.RESOURCES, path='', attributes={}, id='2'),
        ArmBlock(name="name3", config={}, block_type=ArmElements.RESOURCES, path='', attributes={}, id='3')
    ]
    graph.vertices_by_name = {"variables(name1)": 0, "name2": 1, "name3": 2}

    graph._update_resource_vertices_names()

    assert graph.vertices[0].name == "updatedName1"
    assert "name1" not in graph.vertices_by_name
    assert graph.vertices_by_name["updatedName1"] == 0
    assert graph.vertices[1].name == "name2"
    assert graph.vertices[2].name == "name3"

def test_update_vertices_configs():
    graph = ArmLocalGraph(definitions={})
    vertex = MagicMock()
    vertex.changed_attributes = {"attribute1": "value1"}

    graph.vertices = [vertex]

    graph.update_vertex_config = MagicMock()

    graph.update_vertices_configs()

    graph.update_vertex_config.assert_called_once_with(vertex, ['attribute1'])


def test_update_config_attribute_dict():
    config = {"container": {"registry": "initialValue"}}
    ArmLocalGraph.update_config_attribute(config, "container.registry", "newValue")

    assert config['container']['registry'] == "newValue"

def test_adjust_key_exists():
    config = {"container.registry": "value"}
    result = ArmLocalGraph.adjust_key(config, "container", ["container", "registry"])

    assert result == ("container.registry", ["container.registry"])

def test_adjust_key_not_exists():
    config = {}
    result = ArmLocalGraph.adjust_key(config, "none", ["none", "existent"])

    assert result == ("none.existent", ["none.existent"])