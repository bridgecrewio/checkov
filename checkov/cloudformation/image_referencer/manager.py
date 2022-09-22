from __future__ import annotations

from typing import TYPE_CHECKING

from checkov.cloudformation.image_referencer.provider.aws import AwsCloudFormationProvider

if TYPE_CHECKING:
    from checkov.common.images.image_referencer import Image
    from networkx import DiGraph


class CloudFormationImageReferencerManager:
    __slots__ = ("graph_connector",)

    def __init__(self, graph_connector: DiGraph) -> None:
        self.graph_connector = graph_connector

    def extract_images_from_resources(self) -> list[Image]:
        aws_provider = AwsCloudFormationProvider(graph_connector=self.graph_connector)

        images = aws_provider.extract_images_from_resources()

        return images
