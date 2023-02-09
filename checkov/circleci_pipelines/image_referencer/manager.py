from __future__ import annotations
from typing import Any

from checkov.common.images.image_referencer import Image
from checkov.circleci_pipelines.image_referencer.provider import CircleCIProvider


class CircleCIImageReferencerManager:
    __slots__ = ("workflow_config", "file_path")

    def __init__(self, workflow_config: dict[str, Any], file_path: str) -> None:
        self.workflow_config = workflow_config
        self.file_path = file_path

    def extract_images_from_workflow(self) -> list[Image]:
        provider = CircleCIProvider(workflow_config=self.workflow_config, file_path=self.file_path)
        images: list[Image] = provider.extract_images_from_workflow()

        return images
