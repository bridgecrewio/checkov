from __future__ import annotations
from typing import Any
import jmespath

from checkov.common.images.image_referencer import Image
from checkov.common.util.consts import START_LINE, END_LINE


class CircleCIProvider:
    __slots__ = ("workflow_config", "file_path")

    def __init__(self, workflow_config: dict[str, Any], file_path: str) -> None:
        self.file_path = file_path
        self.workflow_config = workflow_config

    def extract_images_from_workflow(self) -> list[Image]:
        images: list[Image] = []

        keywords = (
            "jobs.*.docker[].{image: image, __startline__: __startline__, __endline__:__endline__}",
            "executors.*.docker[].{image: image, __startline__: __startline__, __endline__:__endline__}",
        )
        for keyword in keywords:
            results = jmespath.search(keyword, self.workflow_config)
            if not results:
                continue
            for result in results:
                image_name = result.get("image")
                if image_name:
                    images.append(
                        Image(
                            file_path=self.file_path,
                            name=image_name,
                            start_line=result[START_LINE],
                            end_line=result[END_LINE]
                        )
                    )
        return images
