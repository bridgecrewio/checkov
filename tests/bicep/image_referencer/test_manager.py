from unittest import mock

import pytest

from checkov.bicep.image_referencer.manager import BicepImageReferencerManager
from checkov.common.images.image_referencer import Image
from tests.graph_utils.utils import GRAPH_FRAMEWORKS, set_graph_by_graph_framework, \
    add_vertices_to_graph_by_graph_framework


@pytest.mark.parametrize("graph_framework", GRAPH_FRAMEWORKS)
def test_extract_images_from_resources(graph_framework):
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
                        "password": "myPassword",  # checkov:skip=CKV_SECRET_6 test secret
                        "registryServer": "myContainerRegistry.azurecr.io",
                        "username": "myUserName",
                    },
                    "type": "DockerCompatible",
                },
            }
        },
        "resource_type": "Microsoft.Batch/batchAccounts/pools",
    }
    graph = set_graph_by_graph_framework(graph_framework)
    add_vertices_to_graph_by_graph_framework(graph_framework, resource, graph)


    # when
    with mock.patch.dict('os.environ', {'CHECKOV_GRAPH_FRAMEWORK': graph_framework}):
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
