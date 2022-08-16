from networkx import DiGraph

from checkov.common.images.image_referencer import Image
from checkov.terraform.image_referencer.aws import extract_images_from_aws_resources


def test_extract_images_from_aws_resources():
    # given
    resource = {
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
            {
                "name": "second",
                "image": "python:3.9-alpine",
                "cpu": 10,
                "memory": 256,
                "essential": True,
                "portMappings": [{"containerPort": 443, "hostPort": 443}],
            },
        ],
        "resource_type": "aws_ecs_task_definition",
    }
    graph = DiGraph()
    graph.add_node(1, **resource)

    # when
    images = extract_images_from_aws_resources(graph_connector=graph)

    # then
    assert images == [
        Image(
            file_path="/ecs.tf",
            name="nginx",
            start_line=1,
            end_line=31
        ),
        Image(
            file_path="/ecs.tf",
            name="python:3.9-alpine",
            start_line=1,
            end_line=31
        ),
    ]


def test_extract_images_from_aws_resources_with_no_image():
    # given
    resource = {
        "file_path_": "/ecs.tf",
        "__end_line__": 31,
        "__start_line__": 1,
        "container_definitions": [
            {
                "name": "first",
                "cpu": 10,
                "memory": 512,
                "essential": True,
                "portMappings": [{"containerPort": 80, "hostPort": 80}],
            },
        ],
        "resource_type": "aws_ecs_task_definition",
    }
    graph = DiGraph()
    graph.add_node(1, **resource)

    # when
    images = extract_images_from_aws_resources(graph_connector=graph)

    # then
    assert not images