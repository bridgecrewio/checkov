from __future__ import annotations

from typing import TYPE_CHECKING

from checkov.dockerfile.image_referencer.provider import DockerfileProvider

if TYPE_CHECKING:
    from checkov.common.images.image_referencer import Image
    from dockerfile_parse.parser import _Instruction


class DockerfileImageReferencerManager:
    __slots__ = ("definitions",)

    def __init__(self, definitions: dict[str, dict[str, list[_Instruction]]]) -> None:
        self.definitions = definitions

    def extract_images_from_resources(self) -> list[Image]:
        provider = DockerfileProvider(definitions=self.definitions)

        images = provider.extract_images_from_resources()

        return images
