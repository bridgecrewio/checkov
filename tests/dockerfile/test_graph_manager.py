from pathlib import Path

from checkov.common.graph.db_connectors.networkx.networkx_db_connector import NetworkxConnector
from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.graph.graph_builder.graph_components.block_types import BlockType
from checkov.dockerfile.graph_builder.graph_components.resource_types import ResourceType
from checkov.dockerfile.graph_manager import DockerfileGraphManager
from checkov.dockerfile.utils import get_scannable_file_paths, get_files_definitions

RESOURCES_DIR = Path(__file__).parent / "resources"


def test_build_graph_from_definitions():
    # given
    test_dir_path = RESOURCES_DIR / "expose_port"
    test_file = str(test_dir_path / "pass/Dockerfile")
    files_list = get_scannable_file_paths(root_folder=test_dir_path)
    definitions, _ = get_files_definitions(files_list)

    graph_manager = DockerfileGraphManager(db_connector=NetworkxConnector())

    # when
    local_graph = graph_manager.build_graph_from_definitions(definitions=definitions)

    # then
    assert len(local_graph.vertices) == 16
    assert len(local_graph.edges) == 0

    expose_idx = local_graph.vertices_by_path_and_name[(test_file, ResourceType.EXPOSE)]
    expose = local_graph.vertices[expose_idx]

    assert expose.block_type == BlockType.RESOURCE
    assert expose.id == ResourceType.EXPOSE
    assert expose.source == "Dockerfile"
    assert expose.attributes[CustomAttributes.RESOURCE_TYPE] == ResourceType.EXPOSE
    assert expose.config == {
        "content": "EXPOSE 3000 80 443\n",
        "value": "3000 80 443",
        "__startline__": 2,
        "__endline__": 2,
    }
