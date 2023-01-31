import os
import unittest
from unittest import mock

import igraph
from networkx import DiGraph
from parameterized import parameterized_class

from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.images.image_referencer import Image
from checkov.terraform.image_referencer.provider.gcp import GcpTerraformProvider

@parameterized_class([
   {"graph_framework": "NETWORKX"},
   {"graph_framework": "IGRAPH"}
])
class TestGcp(unittest.TestCase):
    def setUp(self) -> None:
        if self.graph_framework == 'NETWORKX':  # type: ignore
            self.graph = DiGraph()
        elif self.graph_framework == 'IGRAPH':  # type: ignore
            self.graph = igraph.Graph()
        
    def test_extract_images_from_resources(self):
        # given
        resource = {
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
            gcp_provider = GcpTerraformProvider(graph_connector=self.graph)
            images = gcp_provider.extract_images_from_resources()

        # then
        assert images == [
            Image(
                file_path="/cloud_run.tf",
                name="gcr.io/cloudrun/hello",
                start_line=1,
                end_line=17,
                related_resource_id="/cloud_run.tf:None",
            ),
        ]

    def test_extract_images_from_resources_with_no_image(self):
        # given
        resource = {
            "file_path_": "/cloud_run.tf",
            "__end_line__": 17,
            "__start_line__": 1,
            "template": {
                "spec": {
                    "containers": {
                        "working_dir": "/tmp",
                    }
                }
            },
            "resource_type": "google_cloud_run_service",
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
            gcp_provider = GcpTerraformProvider(graph_connector=self.graph)
            images = gcp_provider.extract_images_from_resources()

        # then
        assert not images


if __name__ == '__main__':
    unittest.main()
