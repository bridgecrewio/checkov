from __future__ import annotations
from typing import Any

from checkov.common.images.workflow.image_referencer_manager import WorkflowImageReferencerManager
from checkov.github_actions.image_referencer.provider import GithubActionProvider


class GithubActionsImageReferencerManager(WorkflowImageReferencerManager):
    __slots__ = ("workflow_config", "file_path", "workflow_line_numbers", "provider")

    def __init__(self, workflow_config: dict[str, Any], file_path: str, workflow_line_numbers: list[tuple[int, str]]):
        provider = GithubActionProvider(workflow_config=workflow_config, file_path=file_path,
                                        workflow_line_numbers=workflow_line_numbers)
        super().__init__(workflow_config, file_path, provider)
        self.workflow_line_numbers = workflow_line_numbers
