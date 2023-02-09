from networkx import DiGraph

from checkov.common.images.image_referencer import Image
from checkov.terraform.image_referencer.provider.azure import AzureTerraformProvider


def extract_images_from_resources():
    # given
    resource = {
        "file_path_": "/batch.tf",
        "__end_line__": 25,
        "__start_line__": 1,
        "container_configuration": {
            "container_image_names": ["nginx", "python:3.9-alpine"],
            "container_registries": {
                "password": "myPassword",
                "registry_server": "myContainerRegistry.azurecr.io",
                "user_name": "myUserName",
            },
            "type": "DockerCompatible",
        },
        "resource_type": "azurerm_batch_pool",
    }
    graph = DiGraph()
    graph.add_node(1, **resource)

    # when
    azure_provider = AzureTerraformProvider(graph_connector=graph)
    images = azure_provider.extract_images_from_resources()

    # then
    assert images == [
        Image(file_path="/batch.tf", name="nginx", start_line=1, end_line=25),
        Image(file_path="/batch.tf", name="python:3.9-alpine", start_line=1, end_line=25),
    ]


def test_extract_images_from_resources_with_no_image():
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
    graph = DiGraph()
    graph.add_node(1, **resource)

    # when
    azure_provider = AzureTerraformProvider(graph_connector=graph)
    images = azure_provider.extract_images_from_resources()

    # then
    assert not images
