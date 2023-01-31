import os
import unittest
from unittest import mock

import igraph
from networkx import DiGraph
from parameterized import parameterized_class

from checkov.cloudformation.image_referencer.provider.aws import AwsCloudFormationProvider
from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.images.image_referencer import Image


@parameterized_class([
   {"graph_framework": "NETWORKX"},
   {"graph_framework": "IGRAPH"}
])
class TestAws(unittest.TestCase):
    def setUp(self) -> None:
        if self.graph_framework == 'NETWORKX':  # type: ignore
            self.graph = DiGraph()
        elif self.graph_framework == 'IGRAPH':  # type: ignore
            self.graph = igraph.Graph()

    def test_extract_images_from_resources(self):
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
        if self.graph_framework == 'NETWORKX':
            self.graph.add_node(1, **resource)
        elif self.graph_framework == 'IGRAPH':
            attr = resource
            self.graph.add_vertex(
                name='1',
                block_type_='resource',
                resource_type=attr[CustomAttributes.RESOURCE_TYPE] if CustomAttributes.RESOURCE_TYPE in attr else None,
                attr=attr,
            )

        # when
        with mock.patch.dict('os.environ', {'CHECKOV_GRAPH_FRAMEWORK': self.graph_framework}):
            aws_provider = AwsCloudFormationProvider(graph_connector=self.graph)
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

    def test_extract_images_from_resources_with_no_image(self):
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
        if self.graph_framework == 'NETWORKX':
            self.graph.add_node(1, **resource)
        elif self.graph_framework == 'IGRAPH':
            attr = resource
            self.graph.add_vertex(
                name='1',
                block_type_='resource',
                resource_type=attr[CustomAttributes.RESOURCE_TYPE] if CustomAttributes.RESOURCE_TYPE in attr else None,
                attr=attr,
            )

        # when
        with mock.patch.dict('os.environ', {'CHECKOV_GRAPH_FRAMEWORK': self.graph_framework}):
            aws_provider = AwsCloudFormationProvider(graph_connector=self.graph)
            images = aws_provider.extract_images_from_resources()

        # then
        assert not images


if __name__ == '__main__':
    unittest.main()
