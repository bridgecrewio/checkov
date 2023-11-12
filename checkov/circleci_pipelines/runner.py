from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING, Any, Iterable

from checkov.circleci_pipelines.image_referencer.manager import CircleCIImageReferencerManager
from checkov.common.images.image_referencer import Image, ImageReferencerMixin
from checkov.common.output.report import CheckType, Report
from checkov.circleci_pipelines.registry import registry
from checkov.common.util.type_forcers import force_dict
from checkov.runner_filter import RunnerFilter
from checkov.yaml_doc.runner import Runner as YamlRunner

if TYPE_CHECKING:
    from checkov.common.checks.base_check_registry import BaseCheckRegistry
    from networkx import DiGraph

WORKFLOW_DIRECTORY = "circleci"


class Runner(ImageReferencerMixin["dict[str, dict[str, Any] | list[dict[str, Any]]]"], YamlRunner):
    check_type = CheckType.CIRCLECI_PIPELINES  # noqa: CCE003  # a static attribute

    def require_external_checks(self) -> bool:
        return False

    def import_registry(self) -> BaseCheckRegistry:
        return registry

    def included_paths(self) -> list[str]:
        return [".circleci"]

    @staticmethod
    def _parse_file(
        f: str, file_content: str | None = None
    ) -> tuple[dict[str, Any] | list[dict[str, Any]], list[tuple[int, str]]] | None:
        if Runner.is_workflow_file(f):
            return YamlRunner._parse_file(f)

        return None

    @staticmethod
    def is_workflow_file(file_path: str) -> bool:
        """
        :return: True if the file mentioned is named config.yml/yaml in .circleci dir from included_paths(). Otherwise: False
        """
        abspath = os.path.abspath(file_path)
        return WORKFLOW_DIRECTORY in abspath and abspath.endswith(("config.yml", "config.yaml"))

    def get_resource(self, file_path: str, key: str, supported_entities: Iterable[str],
                     start_line: int = -1, end_line: int = -1, graph_resource: bool = False) -> str:
        """
        supported resources for circleCI:
            jobs.*.docker[].{image: image, __startline__: __startline__, __endline__:__endline__}
            jobs.*.steps[]
            orbs.{orbs: @}
        """
        if len(list(supported_entities)) > 1:
            logging.debug("order of entities might cause extracting the wrong key for resource_id")
        new_key = key
        definition = self.definitions.get(file_path, {})
        if not definition or not isinstance(definition, dict):
            return new_key
        if 'orbs.{orbs: @}' in supported_entities:
            new_key = "orbs"
        elif 'jobs.*.steps[]' in supported_entities:
            job_name = self.resolve_sub_name(definition, start_line, end_line, tag='jobs')
            step_name = self.resolve_step_name(definition['jobs'].get(job_name), start_line, end_line)
            new_key = f'jobs({job_name}).steps{step_name}' if job_name else "jobs"
        elif 'jobs.*.docker[].{image: image, __startline__: __startline__, __endline__:__endline__}' in supported_entities:
            job_name = self.resolve_sub_name(definition, start_line, end_line, tag='jobs')
            image_name = self.resolve_image_name(definition['jobs'].get(job_name), start_line, end_line)
            new_key = f'jobs({job_name}).docker.image{image_name}' if job_name else "jobs"
        elif 'executors.*.docker[].{image: image, __startline__: __startline__, __endline__:__endline__}':
            executor_name = self.resolve_sub_name(definition, start_line, end_line, tag='executors')
            image_name = self.resolve_image_name(definition['executors'].get(executor_name), start_line, end_line)
            new_key = f'executors({executor_name}).docker.image{image_name}' if executor_name else "executors"
        return new_key

    def run(
            self,
            root_folder: str | None = None,
            external_checks_dir: list[str] | None = None,
            files: list[str] | None = None,
            runner_filter: RunnerFilter | None = None,
            collect_skip_comments: bool = True,
    ) -> Report | list[Report]:
        runner_filter = runner_filter or RunnerFilter()
        report = super().run(root_folder=root_folder, external_checks_dir=external_checks_dir,
                             files=files, runner_filter=runner_filter, collect_skip_comments=collect_skip_comments)
        if runner_filter.run_image_referencer:
            if files:
                # 'root_folder' shouldn't be empty to remove the whole path later and only leave the shortened form
                root_folder = os.path.split(os.path.commonprefix(files))[0]

            image_report = self.check_container_image_references(
                root_path=root_folder,
                runner_filter=runner_filter,
                definitions=self.definitions
            )

            if image_report:
                return [report, image_report]  # type:ignore[list-item]  # report can only be of type Report, not a list

        return report

    def extract_images(
        self,
        graph_connector: DiGraph | None = None,
        definitions: dict[str, dict[str, Any] | list[dict[str, Any]]] | None = None,
        definitions_raw: dict[str, list[tuple[int, str]]] | None = None
    ) -> list[Image]:
        images: list[Image] = []
        if not definitions:
            return images

        for file_path, config in definitions.items():
            _config = force_dict(config) or {}
            if not config:
                continue
            manager = CircleCIImageReferencerManager(workflow_config=_config, file_path=file_path)
            images.extend(manager.extract_images_from_workflow())

        return images
