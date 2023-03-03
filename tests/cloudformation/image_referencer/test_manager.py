from unittest import mock

import igraph
import pytest
from networkx import DiGraph

from checkov.cloudformation.image_referencer.manager import CloudFormationImageReferencerManager
from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.images.image_referencer import Image


@pytest.mark.parametrize("graph_framework", ['NETWORKX', 'IGRAPH'])
def test_extract_images_from_resources(graph_framework):
    aws_resource = {
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
                "__startline__": 10,
                "__endline__": 22,
            },
        ],
        "resource_type": "AWS::ECS::TaskDefinition",
    }
    if graph_framework == 'IGRAPH':
        graph = igraph.Graph()
        aws_resource = aws_resource
        graph.add_vertex(
            name='1',
            block_type_='resource',
            resource_type=aws_resource[CustomAttributes.RESOURCE_TYPE] if CustomAttributes.RESOURCE_TYPE in aws_resource else None,
            attr=aws_resource,
        )
    else:
        graph = DiGraph()
        graph.add_node(1, **aws_resource)

    # when
    with mock.patch.dict('os.environ', {'CHECKOV_GRAPH_FRAMEWORK': graph_framework}):
        images = CloudFormationImageReferencerManager(graph_connector=graph).extract_images_from_resources()

    # then
    assert images == [
        Image(file_path="/ecs.yaml", name="amazon/amazon-ecs-sample", start_line=5, end_line=37,
              related_resource_id="/ecs.yaml:None"),
    ]

