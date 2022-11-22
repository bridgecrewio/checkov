from __future__ import annotations

from typing import TYPE_CHECKING

from checkov.bicep.image_referencer.provider.azure import AzureBicepProvider

if TYPE_CHECKING:
    from checkov.common.images.image_referencer import Image
    from networkx import DiGraph


class BicepImageReferencerManager:
    __slots__ = ("graph_connector",)

    def __init__(self, graph_connector: DiGraph) -> None:
        self.graph_connector = graph_connector

    def extract_images_from_resources(self) -> list[Image]:
        bicep_provider = AzureBicepProvider(graph_connector=self.graph_connector)

        images = bicep_provider.extract_images_from_resources()

        return images
