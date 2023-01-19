from __future__ import annotations

from checkov.common.images.workflow.image_referencer_provider import WorkflowImageReferencerProvider

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from checkov.common.images.image_referencer import Image


class WorkflowImageReferencerManager:
    __slots__ = ("workflow_config", "file_path", "provider")

    def __init__(self, workflow_config: dict[str, Any], file_path: str, provider: WorkflowImageReferencerProvider):
        self.workflow_config = workflow_config
        self.file_path = file_path
        self.provider = provider

    def extract_images_from_workflow(self) -> list[Image]:
        images: list[Image] = self.provider.extract_images_from_workflow()
        return images
