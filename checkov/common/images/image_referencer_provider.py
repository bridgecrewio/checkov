from __future__ import annotations

from abc import abstractmethod
from typing import Any

from checkov.common.images.image_referencer import Image


class WorkflowImageReferencerProvider:
    def __init__(self, workflow_config: dict[str, Any], file_path: str):
        self.workflow_config = workflow_config
        self.file_path = file_path

    @staticmethod
    def _get_start_end_lines(entity: dict[str, Any]) -> tuple[int, int]:
        return entity.get('__startline__', 0), entity.get('__endline__', 0)

    @abstractmethod
    def extract_images_from_workflow(self) -> list[Image]:
        pass
