from __future__ import annotations

from typing import Any, cast
import jmespath
from checkov.common.images.image_referencer import Image
from checkov.common.images.workflow.image_referencer_provider import WorkflowImageReferencerProvider
from checkov.common.util.consts import START_LINE, END_LINE
from checkov.yaml_doc.runner import Runner


class CircleCIProvider(WorkflowImageReferencerProvider):
    __slots__ = ("workflow_config", "file_path")

    def __init__(self, workflow_config: dict[str, Any], file_path: str) -> None:
        super().__init__(workflow_config, file_path)

    def generate_resource_key(self, start_line: int, end_line: int, tag: str) -> str:
        sub_name = Runner.resolve_sub_name(self.workflow_config, start_line, end_line, tag)
        if not sub_name:    # Failed to locate the resource in the config file
            return ''
        image_name = Runner.resolve_image_name(self.workflow_config[tag][sub_name], start_line, end_line)
        new_key = f'{tag}({sub_name}).docker.image{image_name}' if sub_name else tag
        return new_key

    def extract_images_from_workflow(self) -> list[Image]:
        images: list[Image] = []

        keywords = (
            ('jobs', "jobs.*.docker[].{image: image, __startline__: __startline__, __endline__:__endline__}"),
            ('executors', "executors.*.docker[].{image: image, __startline__: __startline__, __endline__:__endline__}"),
        )
        for tag, keyword in keywords:
            results = cast("list[dict[str, Any]]", jmespath.search(keyword, self.workflow_config))
            if not results:
                continue
            for result in results:
                image_name = result.get("image")
                if image_name:
                    resource_id = self.generate_resource_key(result[START_LINE], result[END_LINE], tag)
                    if resource_id:
                        images.append(
                            Image(
                                file_path=self.file_path,
                                name=image_name,
                                start_line=result[START_LINE],
                                end_line=result[END_LINE],
                                related_resource_id=resource_id,
                            )
                        )
        return images
