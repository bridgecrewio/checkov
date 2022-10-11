from __future__ import annotations

from typing import TYPE_CHECKING, Any

from checkov.dockerfile.image_referencer.provider import DockerfileProvider

if TYPE_CHECKING:
    from checkov.common.images.image_referencer import Image


class DockerfileImageReferencerManager:
    __slots__ = ("definitions",)

    def __init__(self, definitions: dict[str, Any]) -> None:
        self.definitions = definitions

    def extract_images_from_resources(self) -> list[Image]:
        provider = DockerfileProvider(definitions=self.definitions)

        images = provider.extract_images_from_resources()

        return images
