from __future__ import annotations

from typing import Any

from checkov.common.images.image_referencer import Image
from checkov.common.images.workflow.image_referencer_provider import WorkflowImageReferencerProvider
from checkov.gitlab_ci.common.resource_id_utils import generate_resource_key_recursive


class GitlabCiProvider(WorkflowImageReferencerProvider):

    def __init__(self, workflow_config: dict[str, Any], file_path: str):
        super().__init__(workflow_config, file_path)
        self.supported_keys = ("image", "services")

    def extract_images_from_workflow(self) -> list[Image]:
        images = []
        for job_object in self.workflow_config.values():
            if isinstance(job_object, dict):
                start_line, end_line = GitlabCiProvider._get_start_end_lines(job_object)
                for key, subjob in job_object.items():
                    if key in self.supported_keys:
                        image_name = ""
                        if isinstance(subjob, dict):
                            start_line, end_line = GitlabCiProvider._get_start_end_lines(subjob)
                            image_name = subjob['name']
                        elif isinstance(subjob, str):
                            image_name = subjob
                        elif isinstance(subjob, list):
                            for service in subjob:
                                if isinstance(service, dict):
                                    start_line, end_line = GitlabCiProvider._get_start_end_lines(service)
                                    image_name = service['name']
                                elif isinstance(service, str):
                                    image_name = service
                                if image_name:
                                    image_obj = Image(
                                        file_path=self.file_path,
                                        name=image_name,
                                        start_line=start_line,
                                        end_line=end_line,
                                        related_resource_id=generate_resource_key_recursive(conf=self.workflow_config,
                                                                                            key='',
                                                                                            start_line=start_line,
                                                                                            end_line=end_line)
                                    )
                                    images.append(image_obj)
                                    image_name = ""
                        if image_name:
                            image_obj = Image(
                                file_path=self.file_path,
                                name=image_name,
                                start_line=start_line,
                                end_line=end_line,
                                related_resource_id=generate_resource_key_recursive(conf=self.workflow_config,
                                                                                    key='', start_line=start_line,
                                                                                    end_line=end_line)
                            )
                            images.append(image_obj)
        return images
