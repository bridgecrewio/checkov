import os
import unittest
from unittest import mock

from parameterized import parameterized_class

from checkov.common.images.image_referencer import Image
from checkov.terraform.image_referencer.provider.gcp import GcpTerraformProvider
from tests.graph_utils.utils import set_graph_by_graph_framework, PARAMETERIZED_GRAPH_FRAMEWORKS, \
    add_vertices_to_graph_by_graph_framework


@parameterized_class(PARAMETERIZED_GRAPH_FRAMEWORKS)
class TestGcp(unittest.TestCase):
    def setUp(self) -> None:
        self.graph = set_graph_by_graph_framework(self.graph_framework)

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
        self.graph = set_graph_by_graph_framework(self.graph_framework)
        add_vertices_to_graph_by_graph_framework(self.graph_framework, resource, self.graph)

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
        self.graph = set_graph_by_graph_framework(self.graph_framework)
        add_vertices_to_graph_by_graph_framework(self.graph_framework, resource, self.graph)

        # when
        with mock.patch.dict('os.environ', {'CHECKOV_GRAPH_FRAMEWORK': self.graph_framework}):
            gcp_provider = GcpTerraformProvider(graph_connector=self.graph)
            images = gcp_provider.extract_images_from_resources()

        # then
        assert not images


if __name__ == '__main__':
    unittest.main()
