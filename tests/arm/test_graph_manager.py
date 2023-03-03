from pathlib import Path

import pytest

from checkov.arm.graph_manager import ArmGraphManager
from checkov.arm.utils import get_files_definitions
from checkov.common.graph.db_connectors.igraph.igraph_db_connector import IgraphConnector
from checkov.common.graph.db_connectors.networkx.networkx_db_connector import NetworkxConnector
from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.graph.graph_builder.consts import GraphSource
from checkov.common.graph.graph_builder.graph_components.block_types import BlockType
from checkov.common.util.consts import START_LINE, END_LINE

EXAMPLES_DIR = Path(__file__).parent / "examples"


@pytest.mark.parametrize(
    "graph_connector",
    [
        NetworkxConnector,
        IgraphConnector
    ]
)
def test_build_graph_from_definitions(graph_connector):
    # given
    test_file = str(EXAMPLES_DIR / "container_instance.json")
    definitions, _ = get_files_definitions([test_file])

    graph_manager = ArmGraphManager(db_connector=graph_connector())

    # when
    local_graph = graph_manager.build_graph_from_definitions(definitions=definitions)

    # then
    assert len(local_graph.vertices) == 15
    assert len(local_graph.edges) == 0

    # resource name will change, when variable rendering is supported
    container_idx = local_graph.vertices_by_path_and_id[(test_file, "Microsoft.ContainerInstance/containerGroups.[parameters('containerGroupName')]")]
    container = local_graph.vertices[container_idx]

    assert container.block_type == BlockType.RESOURCE
    assert container.id == "Microsoft.ContainerInstance/containerGroups.[parameters('containerGroupName')]"
    assert container.source == GraphSource.ARM

    assert container.attributes[START_LINE] == 156
    assert container.attributes[END_LINE] == 191
    assert container.attributes[CustomAttributes.RESOURCE_TYPE] == "Microsoft.ContainerInstance/containerGroups"

    assert container.config["type"] == "Microsoft.ContainerInstance/containerGroups"
    assert container.config["apiVersion"] == "2019-12-01"
    assert container.config["name"] == "[parameters('containerGroupName')]"
    assert container.config["location"] == "[parameters('location')]"

    assert container.config["properties"]["osType"] == "Linux"
    assert container.config["properties"]["restartPolicy"] == "Always"
