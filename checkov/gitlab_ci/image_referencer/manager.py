from __future__ import annotations

from typing import Any

from checkov.common.images.workflow.image_referencer_manager import WorkflowImageReferencerManager
from checkov.gitlab_ci.image_referencer.provider import GitlabCiProvider


class GitlabCiImageReferencerManager(WorkflowImageReferencerManager):

    def __init__(self, workflow_config: dict[str, Any], file_path: str):
        provider = GitlabCiProvider(workflow_config=workflow_config, file_path=file_path)
        super().__init__(workflow_config, file_path, provider)
