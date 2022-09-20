from __future__ import annotations

from typing import Any

from checkov.common.images.image_referencer import Image
from checkov.gitlab_ci.image_referencer.base_provider import BaseGitlabCiProvider


class GitlabCiImageReferencerManager:
    __slots__ = ("supported_keys", "workflow_config", "file_path")

    def __init__(self, supported_keys: tuple[str, str], workflow_config: dict[str, Any], file_path: str):
        self.supported_keys = supported_keys
        self.workflow_config = workflow_config
        self.file_path = file_path

    def extract_images_from_workflow(self) -> list[Image]:
        gitlab_base_provider = BaseGitlabCiProvider(supported_keys=self.supported_keys,
                                                    workflow_config=self.workflow_config,
                                                    file_path=self.file_path)

        images: list[Image] = gitlab_base_provider.extract_images_from_workflow()

        return images
