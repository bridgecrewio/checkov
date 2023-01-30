import os

import igraph
import pytest
from networkx import DiGraph

from checkov.bicep.image_referencer.manager import BicepImageReferencerManager
from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.images.image_referencer import Image


@pytest.mark.parametrize("graph_framework", [
    'NETWORKX',
    'IGRAPH',
])
def test_extract_images_from_resources(graph_framework):
    os.environ['CHECKOV_GRAPH_FRAMEWORK'] = graph_framework
    # given
    resource = {
        "file_path_": "/batch.bicep",
        "__end_line__": 26,
        "__start_line__": 1,
        "properties": {
            "virtualMachineConfiguration": {
                "containerConfiguration": {
                    "containerImageNames": ["python:3.9-alpine"],
                    "containerRegistries": {
                        "password": "myPassword",
                        "registryServer": "myContainerRegistry.azurecr.io",
                        "username": "myUserName",
                    },
                    "type": "DockerCompatible",
                },
            }
        },
        "resource_type": "Microsoft.Batch/batchAccounts/pools",
    }
    if graph_framework == 'NETWORKX':
        graph = DiGraph()
        graph.add_node(1, **resource)
    else:
        graph = igraph.Graph()
        attr = resource
        graph.add_vertex(
            name='1',
            block_type_='resource',
            resource_type=attr[CustomAttributes.RESOURCE_TYPE] if CustomAttributes.RESOURCE_TYPE in attr else None,
            attr=attr,
        )

    # when
    images = BicepImageReferencerManager(graph_connector=graph).extract_images_from_resources()

    # then
    assert images == [
        Image(
            file_path="/batch.bicep",
            name="python:3.9-alpine",
            start_line=1,
            end_line=26,
            related_resource_id="/batch.bicep:None",
        ),
    ]
