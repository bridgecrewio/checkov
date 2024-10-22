from unittest import mock

import pytest
from checkov.common.images.image_referencer import Image
from checkov.terraform.image_referencer.provider.azure import AzureTerraformProvider
from tests.graph_utils.utils import GRAPH_FRAMEWORKS, \
    set_graph_by_graph_framework, add_vertices_to_graph_by_graph_framework


@pytest.mark.parametrize("graph_framework", GRAPH_FRAMEWORKS)
def test_extract_images_from_resources(graph_framework):
    # given
    resource = {
        "file_path_": "/batch.tf",
        "__end_line__": 25,
        "__start_line__": 1,
        "container_configuration": {
            "container_image_names": ["nginx", "python:3.9-alpine"],
            "container_registries": {
                "password": "myPassword",  # checkov:skip=CKV_SECRET_6 test secret
                "registry_server": "myContainerRegistry.azurecr.io",
                "user_name": "myUserName",
            },
            "type": "DockerCompatible",
        },
        "resource_type": "azurerm_batch_pool",
    }
    graph = set_graph_by_graph_framework(graph_framework)
    add_vertices_to_graph_by_graph_framework(graph_framework, resource, graph)

    # when
    with mock.patch.dict('os.environ', {'CHECKOV_GRAPH_FRAMEWORK': graph_framework}):
        azure_provider = AzureTerraformProvider(graph_connector=graph)
        images = azure_provider.extract_images_from_resources()

    # then
    assert images == [
        Image(file_path="/batch.tf", name="nginx", start_line=1, end_line=25, related_resource_id='/batch.tf:None'),
        Image(file_path="/batch.tf", name="python:3.9-alpine", start_line=1, end_line=25, related_resource_id='/batch.tf:None'),
    ]


@pytest.mark.parametrize("graph_framework", GRAPH_FRAMEWORKS)
def test_extract_images_from_resources_with_no_image(graph_framework):
    # given
    resource = {
        "file_path_": "/batch.tf",
        "__end_line__": 25,
        "__start_line__": 1,
        "container_configuration": {
            "container_image_names": [],
            "container_registries": {
                "password": "myPassword",
                "registry_server": "myContainerRegistry.azurecr.io",
                "user_name": "myUserName",
            },
            "type": "DockerCompatible",
        },
        "resource_type": "azurerm_batch_pool",
    }
    graph = set_graph_by_graph_framework(graph_framework)
    add_vertices_to_graph_by_graph_framework(graph_framework, resource, graph)

    # when
    with mock.patch.dict('os.environ', {'CHECKOV_GRAPH_FRAMEWORK': graph_framework}):
        azure_provider = AzureTerraformProvider(graph_connector=graph)
        images = azure_provider.extract_images_from_resources()

    # then
    assert not images

