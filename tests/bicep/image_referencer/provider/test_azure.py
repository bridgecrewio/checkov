import os
import unittest
from unittest import mock

import igraph
from networkx import DiGraph
from parameterized import parameterized_class  # type: ignore

from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.images.image_referencer import Image
from checkov.terraform.image_referencer.provider.azure import AzureTerraformProvider


@parameterized_class([
    {"graph_framework": "NETWORKX"},
    {"graph_framework": "IGRAPH"}
])
class TestAzure(unittest.TestCase):
    def setUp(self) -> None:
        self.environ_patch = mock.patch.dict('os.environ', {'CHECKOV_GRAPH_FRAMEWORK': self.graph_framework})
        self.environ_patch.start()
        if self.graph_framework == 'NETWORKX':
            self.graph = DiGraph()
        elif self.graph_framework == 'IGRAPH':
            self.graph = igraph.Graph()

    def test_extract_images_from_resources_with_no_image(self):
        # given
        resource = {
            "file_path_": "/batch.bicep",
            "__end_line__": 26,
            "__start_line__": 1,
            "properties": {
                "virtualMachineConfiguration": {
                    "containerConfiguration": {
                        "containerImageNames": [],
                        "containerRegistries": {
                            "password": "myPassword",
                            "registryServer": "myContainerRegistry.azurecr.io",
                            "username": "myUserName",
                        },
                        "type": "DockerCompatible",
                    },
                }
            },
            "resource_type": "Microsoft.Batch/batchAccounts/pools",
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
        azure_provider = AzureTerraformProvider(graph_connector=self.graph)
        images = azure_provider.extract_images_from_resources()

        # then
        assert not images

    def extract_images_from_resources(self):
        # given
        resource = {
            "file_path_": "/batch.bicep",
            "__end_line__": 26,
            "__start_line__": 1,
            "properties": {
                "virtualMachineConfiguration": {
                    "containerConfiguration": {
                        "containerImageNames": ["nginx", "python:3.9-alpine"],
                        "containerRegistries": {
                            "password": "myPassword",
                            "registryServer": "myContainerRegistry.azurecr.io",
                            "username": "myUserName",
                        },
                        "type": "DockerCompatible",
                    },
                }
            },
            "resource_type": "Microsoft.Batch/batchAccounts/pools",
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
        azure_provider = AzureTerraformProvider(graph_connector=self.graph)
        images = azure_provider.extract_images_from_resources()

        # then
        assert images == [
            Image(file_path="/batch.bicep", name="nginx", start_line=1, end_line=26),
            Image(file_path="/batch.bicep", name="python:3.9-alpine", start_line=1, end_line=26),
        ]


if __name__ == '__main__':
    unittest.main()