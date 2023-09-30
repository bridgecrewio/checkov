from unittest import mock

import pytest
from checkov.common.images.image_referencer import Image
from checkov.terraform.image_referencer.manager import TerraformImageReferencerManager
from tests.graph_utils.utils import set_graph_by_graph_framework, add_vertices_to_graph_by_graph_framework, \
    GRAPH_FRAMEWORKS


@pytest.mark.parametrize("graph_framework", GRAPH_FRAMEWORKS)
def test_extract_images_from_resources(graph_framework):
    # given
    aws_resource = {
        "file_path_": "/ecs.tf",
        "__end_line__": 31,
        "__start_line__": 1,
        "container_definitions": [
            {
                "name": "first",
                "image": "nginx",
                "cpu": 10,
                "memory": 512,
                "essential": True,
                "portMappings": [{"containerPort": 80, "hostPort": 80}],
            },
        ],
        "resource_type": "aws_ecs_task_definition",
    }
    azure_resource = {
        "file_path_": "/batch.tf",
        "__end_line__": 25,
        "__start_line__": 1,
        "container_configuration": {
            "container_image_names": ["python:3.9-alpine"],
            "container_registries": {
                "password": "myPassword",  # checkov:skip=CKV_SECRET_6 test secret
                "registry_server": "myContainerRegistry.azurecr.io",
                "user_name": "myUserName",
            },
            "type": "DockerCompatible",
        },
        "resource_type": "azurerm_batch_pool",
    }
    gcp_resource = {
        "file_path_": "/cloud_run.tf",
        "__end_line__": 17,
        "__start_line__": 1,
        "template": {
            "spec": {
                "containers": {
                    "image": "gcr.io/cloudrun/hello",
                }
            }
        },
        "resource_type": "google_cloud_run_service",
    }
    graph = set_graph_by_graph_framework(graph_framework)
    add_vertices_to_graph_by_graph_framework(graph_framework, aws_resource, graph, 1, 'first')
    add_vertices_to_graph_by_graph_framework(graph_framework, azure_resource, graph, 2, '2')
    add_vertices_to_graph_by_graph_framework(graph_framework, gcp_resource, graph, 3, '3')

    # when
    with mock.patch.dict('os.environ', {'CHECKOV_GRAPH_FRAMEWORK': graph_framework}):
        images = TerraformImageReferencerManager(graph_connector=graph).extract_images_from_resources()

    # then
    assert images == [
        Image(file_path="/ecs.tf", name="nginx", start_line=1, end_line=31, related_resource_id="/ecs.tf:None"),
        Image(
            file_path="/batch.tf",
            name="python:3.9-alpine",
            start_line=1,
            end_line=25,
            related_resource_id="/batch.tf:None",
        ),
        Image(
            file_path="/cloud_run.tf",
            name="gcr.io/cloudrun/hello",
            start_line=1,
            end_line=17,
            related_resource_id="/cloud_run.tf:None",
        ),
    ]

