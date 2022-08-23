from __future__ import annotations

from typing import TYPE_CHECKING

from checkov.terraform.image_referencer.provider.aws import AwsTerraformProvider
from checkov.terraform.image_referencer.provider.azure import AzureTerraformProvider

if TYPE_CHECKING:
    from checkov.common.images.image_referencer import Image
    from networkx import DiGraph


class TerraformImageReferencerManager:
    __slots__ = ("graph_connector",)

    def __init__(self, graph_connector: DiGraph) -> None:
        self.graph_connector = graph_connector

    def extract_images_from_resources(self) -> list[Image]:
        images = []

        aws_provider = AwsTerraformProvider(graph_connector=self.graph_connector)
        azure_provider = AzureTerraformProvider(graph_connector=self.graph_connector)

        images.extend(aws_provider.extract_images_from_resources())
        images.extend(azure_provider.extract_images_from_resources())

        return images
