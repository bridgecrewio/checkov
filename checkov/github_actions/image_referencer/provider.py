from __future__ import annotations
from typing import Any

from checkov.common.images.image_referencer import Image
from checkov.common.util.consts import START_LINE, END_LINE


class GithubActionProvider:
    __slots__ = ("workflow_config", "file_path", "workflow_line_numbers")

    def __init__(self, workflow_config: dict[str, Any], file_path: str, workflow_line_numbers: list[tuple[int, str]]):
        self.workflow_config = workflow_config
        self.file_path = file_path
        self.workflow_line_numbers = workflow_line_numbers

    def generate_resource_key(self, start_line: int, end_line: int) -> str:
        """
        Generate resource key without the previous format of key (needed in get_resource)
        """
        jobs_dict: dict[str, Any] = self.workflow_config.get("jobs", {})
        for job_name, job in jobs_dict.items():
            if not isinstance(job, dict):
                continue

            if job[START_LINE] <= start_line <= end_line <= job[END_LINE]:
                return f'jobs.{job_name}'

        return ''

    def extract_images_from_workflow(self) -> list[Image]:
        images: list[Image] = []

        if not isinstance(self.workflow_config, dict):
            # make type checking happy
            return images

        jobs = self.workflow_config.get("jobs", {})
        for job_object in jobs.values():
            if isinstance(job_object, dict):
                container = job_object.get("container", {})
                image = None
                start_line = 0
                end_line = 0

                if isinstance(container, dict):
                    image = container.get("image", "")
                    start_line, end_line = container.get(START_LINE, 0), container.get(END_LINE, 0)

                elif isinstance(container, str):
                    image = container
                    start_line = [line_number for line_number, line in self.workflow_line_numbers if image in line][0]
                    end_line = start_line + 1

                if image:
                    image_obj = Image(
                        file_path=self.file_path[self.file_path.index('/.github'):],
                        name=image,
                        start_line=start_line,
                        end_line=end_line,
                        related_resource_id=self.generate_resource_key(start_line, end_line)
                    )
                    images.append(image_obj)

        return images
