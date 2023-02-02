
from unittest import mock

import igraph
import pytest
from networkx import DiGraph

from checkov.cloudformation.image_referencer.provider.aws import AwsCloudFormationProvider
from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.images.image_referencer import Image


@pytest.mark.parametrize("graph_framework", ['NETWORKX', 'IGRAPH'])
def test_extract_images_from_resources(graph_framework):
    # given
    resource = {
        "file_path_": "/ecs.yaml",
        "__endline__": 37,
        "__startline__": 5,
        "ContainerDefinitions": [
            {
                "Name": "my-app",
                "Image": "amazon/amazon-ecs-sample",
                "Cpu": 256,
                "EntryPoint": ["/usr/sbin/apache2", "-D", "FOREGROUND"],
                "Memory": 512,
                "Essential": True,
            },
            {
                "Name": "busybox",
                "Image": "busybox",
                "Cpu": 256,
                "EntryPoint": ["sh", "-c"],
                "Memory": 512,
                "Command": ['/bin/sh -c "while true; do /bin/date > /var/www/my-vol/date; sleep 1; done"'],
                "Essential": False,
            },
        ],
        "resource_type": "AWS::ECS::TaskDefinition",
    }
    if graph_framework == 'IGRAPH':
        graph = igraph.Graph()
        attr = resource
        graph.add_vertex(
            name='1',
            block_type_='resource',
            resource_type=attr[CustomAttributes.RESOURCE_TYPE] if CustomAttributes.RESOURCE_TYPE in attr else None,
            attr=attr,
        )
    else:
        graph = DiGraph()
        graph.add_node(1, **resource)

    # when
    with mock.patch.dict('os.environ', {'CHECKOV_GRAPH_FRAMEWORK': graph_framework}):
        aws_provider = AwsCloudFormationProvider(graph_connector=graph)
        images = aws_provider.extract_images_from_resources()

    # then
    assert images == [
        Image(
            file_path="/ecs.yaml",
            name="amazon/amazon-ecs-sample",
            start_line=5,
            end_line=37,
            related_resource_id="/ecs.yaml:None",
        ),
        Image(file_path="/ecs.yaml", name="busybox", start_line=5, end_line=37, related_resource_id="/ecs.yaml:None"),
    ]


@pytest.mark.parametrize("graph_framework", ['NETWORKX', 'IGRAPH'])
def test_extract_images_from_resources_with_no_image(graph_framework):
    # given
    resource = {
        "file_path_": "/ecs.yaml",
        "__endline__": 37,
        "__startline__": 5,
        "ContainerDefinitions": [
            {
                "Name": "my-app",
                "Cpu": 256,
                "EntryPoint": ["/usr/sbin/apache2", "-D", "FOREGROUND"],
                "Memory": 512,
                "Essential": True,
            },
        ],
        "resource_type": "AWS::ECS::TaskDefinition",
    }
    if graph_framework == 'IGRAPH':
        graph = igraph.Graph()
        attr = resource
        graph.add_vertex(
            name='1',
            block_type_='resource',
            resource_type=attr[CustomAttributes.RESOURCE_TYPE] if CustomAttributes.RESOURCE_TYPE in attr else None,
            attr=attr,
        )
    else:
        graph = DiGraph()
        graph.add_node(1, **resource)

    # when
    with mock.patch.dict('os.environ', {'CHECKOV_GRAPH_FRAMEWORK': graph_framework}):
        aws_provider = AwsCloudFormationProvider(graph_connector=graph)
        images = aws_provider.extract_images_from_resources()

    # then
    assert not images

