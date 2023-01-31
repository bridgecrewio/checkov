import os
import unittest
from unittest import mock

import igraph
from networkx import DiGraph
from parameterized import parameterized_class

from checkov.cloudformation.image_referencer.manager import CloudFormationImageReferencerManager
from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.images.image_referencer import Image


@parameterized_class([
    {"graph_framework": "NETWORKX"},
    {"graph_framework": "IGRAPH"}
])
class TestManager(unittest.TestCase):
    def setUp(self) -> None:
        self.environ_patch = mock.patch.dict('os.environ', {'CHECKOV_GRAPH_FRAMEWORK': self.graph_framework})
        self.environ_patch.start()
        if self.graph_framework == 'NETWORKX':
            self.graph = DiGraph()
        elif self.graph_framework == 'IGRAPH':
            self.graph = igraph.Graph()

    def test_extract_images_from_resources(self):
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
        if self.graph_framework == 'NETWORKX':
            self.graph.add_node(1, **aws_resource)
        elif self.graph_framework == 'IGRAPH':
            aws_resource = aws_resource
            self.graph.add_vertex(
                name='1',
                block_type_='resource',
                resource_type=aws_resource[CustomAttributes.RESOURCE_TYPE] if CustomAttributes.RESOURCE_TYPE in aws_resource else None,
                attr=aws_resource,
            )

        # when
        images = CloudFormationImageReferencerManager(graph_connector=self.graph).extract_images_from_resources()

        # then
        assert images == [
            Image(file_path="/ecs.yaml", name="amazon/amazon-ecs-sample", start_line=5, end_line=37,
                  related_resource_id="/ecs.yaml:None"),
        ]


if __name__ == '__main__':
    unittest.main()
