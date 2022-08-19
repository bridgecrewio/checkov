from __future__ import annotations

from typing import TYPE_CHECKING

from checkov.terraform.image_referencer.aws import extract_images_from_aws_resources
from checkov.terraform.image_referencer.azure import extract_images_from_azure_resources

if TYPE_CHECKING:
    from checkov.common.images.image_referencer import Image
    from networkx import DiGraph


class TerraformImageReferencerManager:
    __slots__ = ("graph_connector",)

    def __init__(self, graph_connector: DiGraph) -> None:
        self.graph_connector = graph_connector

    def extract_images_from_resources(self) -> list[Image]:
        images = []

        images.extend(extract_images_from_aws_resources(graph_connector=self.graph_connector))
        images.extend(extract_images_from_azure_resources(graph_connector=self.graph_connector))

        return images
