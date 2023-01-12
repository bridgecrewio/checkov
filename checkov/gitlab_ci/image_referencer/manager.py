from __future__ import annotations

from typing import Any

from checkov.common.images.image_referencer_manager import ImageReferencerManager
from checkov.gitlab_ci.image_referencer.provider import GitlabCiProvider


class GitlabCiImageReferencerManager(ImageReferencerManager):
    __slots__ = ("workflow_config", "file_path", "provider")

    def __init__(self, workflow_config: dict[str, Any], file_path: str):
        super().__init__(workflow_config, file_path)
        self.provider = GitlabCiProvider(workflow_config=self.workflow_config, file_path=self.file_path)
