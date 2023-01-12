from __future__ import annotations
from typing import Any

from checkov.common.images.image_referencer_manager import ImageReferencerManager
from checkov.github_actions.image_referencer.provider import GithubActionProvider


class GithubActionsImageReferencerManager(ImageReferencerManager):
    __slots__ = ("workflow_config", "file_path", "workflow_line_numbers", "provider")

    def __init__(self, workflow_config: dict[str, Any], file_path: str, workflow_line_numbers: list[tuple[int, str]]):
        super().__init__(workflow_config, file_path)
        self.workflow_line_numbers = workflow_line_numbers
        self.provider = GithubActionProvider(workflow_config=self.workflow_config, file_path=self.file_path,
                                             workflow_line_numbers=self.workflow_line_numbers)
