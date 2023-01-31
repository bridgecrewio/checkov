import os
import unittest
from unittest import mock

import igraph
from networkx import DiGraph
from parameterized import parameterized_class

from checkov.common.graph.graph_builder import CustomAttributes
from checkov.kubernetes.image_referencer.manager import KubernetesImageReferencerManager
from checkov.common.images.image_referencer import Image

@parameterized_class([
    {"graph_framework": "NETWORKX"},
    {"graph_framework": "IGRAPH"}
])
class TestManager(unittest.TestCase):
    def setUp(self) -> None:
        if self.graph_framework == 'NETWORKX':
            self.graph = DiGraph()
        elif self.graph_framework == 'IGRAPH':
            self.graph = igraph.Graph()

    def test_extract_images_from_resources(self):
        # given
        resource = {
            "file_path_": "/pod.yaml",
            "__endline__": 16,
            "__startline__": 1,
            "spec": {
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
            self.graph.add_vertex(
                name='1',
                block_type_='resource',
                resource_type=resource[
                    CustomAttributes.RESOURCE_TYPE] if CustomAttributes.RESOURCE_TYPE in resource else None,
                attr=resource,
            )

        # when
        with mock.patch.dict('os.environ', {'CHECKOV_GRAPH_FRAMEWORK': self.graph_framework}):
            images = KubernetesImageReferencerManager(graph_connector=self.graph).extract_images_from_resources()

        # then
        assert images == [
            Image(
                file_path="/pod.yaml",
                name="nginx",
                start_line=1,
                end_line=16,
                related_resource_id="/pod.yaml:None",
            ),
        ]


if __name__ == '__main__':
    unittest.main()
