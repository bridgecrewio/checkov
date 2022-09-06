from __future__ import annotations

from typing import TYPE_CHECKING, Any

from checkov.common.images.image_referencer import ImageReferencer, Image
from checkov.common.bridgecrew.check_type import CheckType
from checkov.gitlab_ci.checks.registry import registry
from checkov.yaml_doc.runner import Runner as YamlRunner

if TYPE_CHECKING:
    from checkov.common.checks.base_check_registry import BaseCheckRegistry
    from collections.abc import Iterable


class Runner(YamlRunner, ImageReferencer):
    check_type = CheckType.GITLAB_CI  # noqa: CCE003  # a static attribute

    def __init__(self) -> None:
        super().__init__()

    def require_external_checks(self) -> bool:
        return False

    def import_registry(self) -> BaseCheckRegistry:
        return registry

    def _parse_file(
        self, f: str, file_content: str | None = None
    ) -> tuple[dict[str, Any] | list[dict[str, Any]], list[tuple[int, str]]] | None:
        if self.is_workflow_file(f):
            return super()._parse_file(f=f, file_content=file_content)

    def is_workflow_file(self, file_path: str) -> bool:
        """
        :return: True if the file mentioned is in the gitlab workflow name .gitlab-ci.yml. Otherwise: False
        """
        return file_path.endswith((".gitlab-ci.yml", ".gitlab-ci.yaml"))

    def included_paths(self) -> Iterable[str]:
        return (".gitlab-ci.yml", ".gitlab-ci.yaml")

    def get_images(self, file_path: str) -> set[Image]:
        """
        Get container images mentioned in a file
        :param file_path: File to be inspected
        GitLab a workflow file can have a job and services run within a container.

        in the following sample file we can see a node:14.16 image:

        default:
            image:
                name: ruby:2.6
                entrypoint: ["/bin/bash"]

            image: nginx:1.18

            services:
                - name: privateregistry/stuff/my-postgres:11.7
                  alias: db-postgres
                - name: redis:latest
                - nginx:1.17
        Source: https://docs.gitlab.com/ee/ci/docker/using_docker_images.html

        :return: List of container image short ids mentioned in the file.
        Example return value for a file with node:14.16 image: ['sha256:6a353e22ce']
        """

        images = set()
        imagesKeys = ("image", "services")
        workflow, workflow_line_numbers = self._parse_file(file_path)

        for job_object in workflow.values():
            if isinstance(job_object, dict):
                start_line = job_object.get('__startline__', 0)
                end_line = job_object.get('__endline__', 0)
                for key, subjob in job_object.items():
                    if key in imagesKeys:
                        imagename = ""
                        if isinstance(subjob, dict):
                            start_line = subjob.get('__startline__', 0)
                            end_line = subjob.get('__endline__', 0)
                            imagename = subjob['name']
                        elif isinstance(subjob, str):
                            imagename = subjob
                        elif isinstance(subjob, list):
                            for service in subjob:
                                if isinstance(service, dict):
                                    start_line = service.get('__startline__', 0)
                                    end_line = service.get('__endline__', 0)
                                    imagename = service['name']
                                elif isinstance(service, str):
                                    imagename = service
                                if imagename:
                                    image_obj = Image(
                                        file_path=file_path,
                                        name=imagename,
                                        start_line=start_line,
                                        end_line=end_line,
                                    )
                                    images.add(image_obj)
                                    imagename = ""
                        if imagename:
                            image_obj = Image(
                                file_path=file_path,
                                name=imagename,
                                start_line=start_line,
                                end_line=end_line,
                            )
                            images.add(image_obj)
                            imagename = ""
        return images
