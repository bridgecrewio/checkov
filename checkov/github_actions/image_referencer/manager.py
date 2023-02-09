from __future__ import annotations
from typing import Any

from checkov.common.images.image_referencer import Image
from checkov.github_actions.image_referencer.provider import GithubActionProvider


class GithubActionsImageReferencerManager:
    __slots__ = ("workflow_config", "file_path", "workflow_line_numbers")

    def __init__(self, workflow_config: dict[str, Any], file_path: str, workflow_line_numbers: list[tuple[int, str]]):
        self.workflow_config = workflow_config
        self.file_path = file_path
        self.workflow_line_numbers = workflow_line_numbers

    def extract_images_from_workflow(self) -> list[Image]:
        provider = GithubActionProvider(workflow_config=self.workflow_config, file_path=self.file_path,
                                        workflow_line_numbers=self.workflow_line_numbers)
        images: list[Image] = provider.extract_images_from_workflow()

        return images
