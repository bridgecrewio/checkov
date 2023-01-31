import unittest
from unittest import mock

import igraph
from networkx import DiGraph
from parameterized import parameterized_class

from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.images.image_referencer import Image
from checkov.terraform.image_referencer.provider.azure import AzureTerraformProvider


@parameterized_class([
   {"graph_framework": "NETWORKX"},
   {"graph_framework": "IGRAPH"}
])
class TestAzure(unittest.TestCase):
    def setUp(self) -> None:
        if self.graph_framework == 'NETWORKX':  # type: ignore
            self.graph = DiGraph()
        elif self.graph_framework == 'IGRAPH':  # type: ignore
            self.graph = igraph.Graph()

    def test_extract_images_from_resources(self):
        # given
        resource = {
            "file_path_": "/batch.tf",
            "__end_line__": 25,
            "__start_line__": 1,
            "container_configuration": {
                "container_image_names": ["nginx", "python:3.9-alpine"],
                "container_registries": {
                    "password": "myPassword",
                    "registry_server": "myContainerRegistry.azurecr.io",
                    "user_name": "myUserName",
                },
                "type": "DockerCompatible",
            },
            "resource_type": "azurerm_batch_pool",
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
            azure_provider = AzureTerraformProvider(graph_connector=self.graph)
            images = azure_provider.extract_images_from_resources()

        # then
        assert images == [
            Image(file_path="/batch.tf", name="nginx", start_line=1, end_line=25, related_resource_id='/batch.tf:None'),
            Image(file_path="/batch.tf", name="python:3.9-alpine", start_line=1, end_line=25, related_resource_id='/batch.tf:None'),
        ]

    def test_extract_images_from_resources_with_no_image(self):
        # given
        resource = {
            "file_path_": "/batch.tf",
            "__end_line__": 25,
            "__start_line__": 1,
            "container_configuration": {
                "container_image_names": [],
                "container_registries": {
                    "password": "myPassword",
                    "registry_server": "myContainerRegistry.azurecr.io",
                    "user_name": "myUserName",
                },
                "type": "DockerCompatible",
            },
            "resource_type": "azurerm_batch_pool",
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
            azure_provider = AzureTerraformProvider(graph_connector=self.graph)
            images = azure_provider.extract_images_from_resources()

        # then
        assert not images


if __name__ == '__main__':
    unittest.main()
