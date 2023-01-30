import os
import unittest

import igraph
from networkx import DiGraph
from parameterized import parameterized_class

from checkov.common.graph.graph_builder import CustomAttributes
from checkov.kubernetes.image_referencer.provider.k8s import KubernetesProvider
from checkov.common.images.image_referencer import Image


@parameterized_class([
   {"graph_framework": "NETWORKX"},
   {"graph_framework": "IGRAPH"}
])
class TestK8S(unittest.TestCase):
    def setUp(self) -> None:
        os.environ['CHECKOV_GRAPH_FRAMEWORK'] = self.graph_framework
        if self.graph_framework == 'NETWORKX':  # type: ignore
            self.graph = DiGraph()
        elif self.graph_framework == 'IGRAPH':  # type: ignore
            self.graph = igraph.Graph()

    def test_extract_images_from_resources(self):
        # given
        resource = {
            "file_path_": "/pod.yaml",
            "__endline__": 16,
            "__startline__": 1,
            "spec": {
                "initContainers": [
                    {
                        "name": "init-sysctl",
                        "image": "busybox",
                    },
                ],
                "containers": [
                    {
                        "name": "test-container",
                        "image": "nginx",
                    },
                ],
            },
            "resource_type": "Pod",
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
        provider = KubernetesProvider(graph_connector=self.graph)
        images = provider.extract_images_from_resources()

        # then
        assert images == [
            Image(
                file_path="/pod.yaml",
                name="nginx",
                start_line=1,
                end_line=16,
                related_resource_id="/pod.yaml:None",
            ),
            Image(file_path="/pod.yaml", name="busybox", start_line=1, end_line=16, related_resource_id="/pod.yaml:None"),
        ]

    def test_extract_images_from_resources_with_no_image(self):
        # given
        resource = {
            "file_path_": "/pod.yaml",
            "__endline__": 16,
            "__startline__": 1,
            "spec": {
                "containers": [
                    {
                        "name": "test-container",
                    },
                ],
            },
            "resource_type": "Pod",
        }
        if self.graph_framework == 'NETWORKX':
            self.graph.add_node(1, **resource)
        elif self.graph_framework == 'IGRAPH':
            self.graph.add_vertex(
                name='1',
                block_type_='resource',
                resource_type=resource[CustomAttributes.RESOURCE_TYPE] if CustomAttributes.RESOURCE_TYPE in resource else None,
                attr=resource,
            )

        # when
        provider = KubernetesProvider(graph_connector=self.graph)
        images = provider.extract_images_from_resources()

        # then
        assert not images


if __name__ == '__main__':
    unittest.main()