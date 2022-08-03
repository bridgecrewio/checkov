from __future__ import annotations

import os
from collections.abc import Iterable
from typing import TYPE_CHECKING, Any, cast

from checkov.common.images.image_referencer import ImageReferencer, Image
from checkov.common.output.report import CheckType
from checkov.common.util.consts import START_LINE, END_LINE
from checkov.github_actions.checks.registry import registry
from checkov.yaml_doc.runner import Runner as YamlRunner

if TYPE_CHECKING:
    from checkov.common.checks.base_check_registry import BaseCheckRegistry

WORKFLOW_DIRECTORY = ".github/workflows/"


class Runner(YamlRunner, ImageReferencer):
    check_type = CheckType.GITHUB_ACTIONS  # noqa: CCE003  # a static attribute

    def __init__(self):
        super().__init__()

    def require_external_checks(self) -> bool:
        return False

    def import_registry(self) -> BaseCheckRegistry:
        return registry

    def _parse_file(
        self, f: str, file_content: str | None = None
    ) -> tuple[dict[str, Any] | list[dict[str, Any]], list[tuple[int, str]]] | None:
        if self.is_workflow_file(f):
            return super()._parse_file(f)

        return None

    def is_workflow_file(self, file_path: str) -> bool:
        """
        :return: True if the file mentioned is in a github action workflow directory and is a YAML file. Otherwise: False
        """
        abspath = os.path.abspath(file_path)
        return WORKFLOW_DIRECTORY in abspath and abspath.endswith(("yml", "yaml"))

    def included_paths(self) -> Iterable[str]:
        return [".github"]

    def get_resource(self, file_path: str, key: str, supported_entities: Iterable[str], definitions: dict[str, Any] | None = None) -> str:
        if not definitions:
            return key

        potential_job_name = key.split('.')[1]
        if potential_job_name != '*':
            new_key = f'jobs.{potential_job_name}'
        else:
            start_line, end_line = Runner.get_start_and_end_lines(key)
            job_name = Runner.resolve_job_name(definitions, start_line, end_line)
            step_name = Runner.resolve_step_name(definitions["jobs"][job_name], start_line, end_line)
            new_key = f'jobs.{job_name}.steps.{step_name}'
        return new_key

    def get_images(self, file_path: str) -> set[Image]:
        """
        Get container images mentioned in a file
        :param file_path: File to be inspected
        GitHub actions workflow file can have a job run within a container.

        in the following sample file we can see a node:14.16 image:

        # jobs:
        #   my_job:
        #     container:
        #       image: node:14.16
        #       env:
        #         NODE_ENV: development
        #       ports:
        #         - 80
        #       volumes:
        #         - my_docker_volume:/volume_mount
        #       options: --cpus 1
        Source: https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions#example-defining-credentials-for-a-container-registry

        :return: List of container image classes ids mentioned in the file.
        """

        images: set[Image] = set()
        parsed_file = self._parse_file(file_path)

        if not parsed_file:
            return images

        workflow, workflow_line_numbers = parsed_file

        if not isinstance(workflow, dict):
            # make type checking happy
            return images

        jobs = workflow.get("jobs", {})
        for job_object in jobs.values():
            if isinstance(job_object, dict):
                container = job_object.get("container", {})
                image = None
                start_line = container.get('__startline__', 0)
                end_line = container.get('__endline__', 0)
                if isinstance(container, dict):
                    image = container.get("image", "")
                elif isinstance(container, str):
                    image = container
                if image:
                    image_obj = Image(
                        file_path=file_path,
                        name=image,
                        start_line=start_line,
                        end_line=end_line,
                    )
                    images.add(image_obj)

        return images

    @staticmethod
    def get_start_and_end_lines(key: str) -> list[int]:
        check_name = key.split('.')[-1]
        try:
            start_end_line_bracket_index = check_name.index('[')
        except ValueError:
            return [-1, -1]
        return [int(x) for x in check_name[start_end_line_bracket_index + 1: len(check_name) - 1].split(':')]

    @staticmethod
    def resolve_job_name(definition: dict[str, Any], start_line: int, end_line: int) -> str:
        for key, job in definition.get('jobs', {}).items():
            if key in [START_LINE, END_LINE]:
                continue
            if job[START_LINE] <= start_line <= end_line <= job[END_LINE]:
                return str(key)
        return ""

    @staticmethod
    def resolve_step_name(job_definition: dict[str, Any], start_line: int, end_line: int) -> str:
        for step in job_definition.get('steps', {}):
            if step[START_LINE] <= start_line <= end_line <= step[END_LINE]:
                try:
                    name = step["name"]
                except KeyError:
                    name = step[next(iter(step.keys()))]

                return cast(str, name)

        return ""
