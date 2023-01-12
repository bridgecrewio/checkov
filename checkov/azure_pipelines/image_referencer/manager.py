from __future__ import annotations

from typing import Any

from checkov.azure_pipelines.image_referencer.provider import AzurePipelinesProvider
from checkov.common.images.image_referencer_manager import ImageReferencerManager


class AzurePipelinesImageReferencerManager(ImageReferencerManager):
    __slots__ = ("workflow_config", "file_path", "provider")

    def __init__(self, workflow_config: dict[str, Any], file_path: str):
        provider = AzurePipelinesProvider(workflow_config=self.workflow_config, file_path=self.file_path)
        super().__init__(workflow_config, file_path, provider)
