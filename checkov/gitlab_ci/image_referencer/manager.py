from __future__ import annotations

from typing import Any

from checkov.common.images.image_referencer import Image
from checkov.gitlab_ci.image_referencer.provider import GitlabCiProvider


class GitlabCiImageReferencerManager:
    __slots__ = ("workflow_config", "file_path")

    def __init__(self, workflow_config: dict[str, Any], file_path: str):
        self.workflow_config = workflow_config
        self.file_path = file_path

    def extract_images_from_workflow(self) -> list[Image]:
        gitlab_provider = GitlabCiProvider(workflow_config=self.workflow_config, file_path=self.file_path)
        images: list[Image] = gitlab_provider.extract_images_from_workflow()

        return images
