from networkx import DiGraph

from checkov.common.images.image_referencer import Image
from checkov.terraform.image_referencer.manager import TerraformImageReferencerManager


def test_extract_images_from_resources():
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
                "password": "myPassword",
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
    graph = DiGraph()
    graph.add_node(1, **aws_resource)
    graph.add_node(2, **azure_resource)
    graph.add_node(3, **gcp_resource)

    # when
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
