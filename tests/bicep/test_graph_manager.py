from pathlib import Path

from checkov.bicep.graph_manager import BicepGraphManager
from checkov.bicep.parser import Parser
from checkov.common.graph.db_connectors.networkx.networkx_db_connector import NetworkxConnector
from checkov.common.graph.graph_builder.graph_components.block_types import BlockType

EXAMPLES_DIR = Path(__file__).parent / "examples"


def test_build_graph_from_source_directory():
    # given
    existing_file = EXAMPLES_DIR / "existing.bicep"
    playground_file = EXAMPLES_DIR / "playground.bicep"
    graph_file = EXAMPLES_DIR / "graph.bicep"
    loop_file = EXAMPLES_DIR / "loop.bicep"
    graph_manager = BicepGraphManager(db_connector=NetworkxConnector())

    # when
    local_graph, definitions = graph_manager.build_graph_from_source_directory(source_dir=str(EXAMPLES_DIR))

    # then
    assert set(definitions.keys()) == {existing_file, playground_file, graph_file, loop_file}  # should not include 'malformed.bicep' file

    assert len(local_graph.vertices) == 48
    assert len(local_graph.edges) == 42

    storage_account_idx = local_graph.vertices_by_name["diagsAccount"]  # vertices_by_name exists for BicepGraphManager
    storage_account = local_graph.vertices[storage_account_idx]

    assert storage_account.block_type == BlockType.RESOURCE
    assert storage_account.id == "Microsoft.Storage/storageAccounts.diagsAccount"
    assert storage_account.source == "Bicep"
    assert storage_account.config == {
        "decorators": [],
        "type": "Microsoft.Storage/storageAccounts",
        "api_version": "2019-06-01",
        "existing": False,
        "config": {
            "name": "diags${uniqueString(resourceGroup().id)}",
            "location": {
                "function": {
                    "type": "resource_group",
                    "parameters": {"resource_group_name": None, "subscription_id": None},
                    "property_name": "location",
                }
            },
            "sku": {"name": "Standard_LRS"},
            "kind": "StorageV2",
        },
        "__start_line__": 84,
        "__end_line__": 92,
    }


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
    assert storage_account.config == {
        "decorators": [],
        "type": "Microsoft.Storage/storageAccounts",
        "api_version": "2019-06-01",
        "existing": False,
        "config": {
            "name": "diags${uniqueString(resourceGroup().id)}",
            "location": {
                "function": {
                    "type": "resource_group",
                    "parameters": {"resource_group_name": None, "subscription_id": None},
                    "property_name": "location",
                }
            },
            "sku": {"name": "Standard_LRS"},
            "kind": "StorageV2",
        },
        "__start_line__": 84,
        "__end_line__": 92,
    }
