from pathlib import Path

from checkov.bicep.graph_manager import BicepGraphManager
from checkov.bicep.parser import Parser
from checkov.common.graph.db_connectors.networkx.networkx_db_connector import NetworkxConnector
from checkov.common.graph.graph_builder.graph_components.block_types import BlockType

EXAMPLES_DIR = Path(__file__).parent / "examples"


def test_build_graph_from_source_directory():
    # given
    test_file = EXAMPLES_DIR / "playground.bicep"
    graph_manager = BicepGraphManager(db_connector=NetworkxConnector())

    # when
    local_graph, definitions = graph_manager.build_graph_from_source_directory(source_dir=str(EXAMPLES_DIR))

    # then
    assert list(definitions.keys()) == [test_file]  # should no include 'malformed.bicep' file

    assert len(local_graph.vertices) == 24
    assert len(local_graph.edges) == 29

    storage_account_idx = local_graph.vertices_by_name["diagsAccount"]  # vertices_by_name exists for BicepGraphManager
    storage_account = local_graph.vertices[storage_account_idx]

    assert storage_account.block_type == BlockType.RESOURCE
    assert storage_account.id == "Microsoft.Storage/storageAccounts.diagsAccount"
    assert storage_account.source == "Bicep"
    assert storage_account.config == definitions[test_file]["resources"]["diagsAccount"]


def test_build_graph_from_definitions():
    # given
    test_file = EXAMPLES_DIR / "playground.bicep"
    graph_manager = BicepGraphManager(db_connector=NetworkxConnector())
    template, _ = Parser().parse(test_file)

    # when
    local_graph = graph_manager.build_graph_from_definitions(definitions={test_file: template})

    # then
    assert len(local_graph.vertices) == 24
    assert len(local_graph.edges) == 29

    storage_account_idx = local_graph.vertices_by_name["diagsAccount"]  # vertices_by_name exists for BicepGraphManager
    storage_account = local_graph.vertices[storage_account_idx]

    assert storage_account.block_type == BlockType.RESOURCE
    assert storage_account.id == "Microsoft.Storage/storageAccounts.diagsAccount"
    assert storage_account.source == "Bicep"
    assert storage_account.config == template["resources"]["diagsAccount"]
