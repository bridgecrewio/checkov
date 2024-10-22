from __future__ import annotations

from typing import TYPE_CHECKING

from checkov.common.images.graph.image_referencer_manager import GraphImageReferencerManager
from checkov.terraform.image_referencer.provider.aws import AwsTerraformProvider
from checkov.terraform.image_referencer.provider.azure import AzureTerraformProvider
from checkov.terraform.image_referencer.provider.gcp import GcpTerraformProvider

if TYPE_CHECKING:
    from checkov.common.images.image_referencer import Image


class TerraformImageReferencerManager(GraphImageReferencerManager):

    def extract_images_from_resources(self) -> list[Image]:
        images = []

        aws_provider = AwsTerraformProvider(graph_connector=self.graph_connector)
        azure_provider = AzureTerraformProvider(graph_connector=self.graph_connector)
        gcp_provider = GcpTerraformProvider(graph_connector=self.graph_connector)

        images.extend(aws_provider.extract_images_from_resources())
        images.extend(azure_provider.extract_images_from_resources())
        images.extend(gcp_provider.extract_images_from_resources())

        return images
