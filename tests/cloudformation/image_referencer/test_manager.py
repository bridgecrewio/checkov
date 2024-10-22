from unittest import mock

import pytest

from checkov.cloudformation.image_referencer.manager import CloudFormationImageReferencerManager
from checkov.common.images.image_referencer import Image
from tests.graph_utils.utils import set_graph_by_graph_framework, add_vertices_to_graph_by_graph_framework, \
    GRAPH_FRAMEWORKS


@pytest.mark.parametrize("graph_framework", GRAPH_FRAMEWORKS)
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
    graph = set_graph_by_graph_framework(graph_framework)
    add_vertices_to_graph_by_graph_framework(graph_framework, aws_resource, graph)

    # when
    with mock.patch.dict('os.environ', {'CHECKOV_GRAPH_FRAMEWORK': graph_framework}):
        images = CloudFormationImageReferencerManager(graph_connector=graph).extract_images_from_resources()

    # then
    assert images == [
        Image(file_path="/ecs.yaml", name="amazon/amazon-ecs-sample", start_line=5, end_line=37,
              related_resource_id="/ecs.yaml:None"),
    ]

