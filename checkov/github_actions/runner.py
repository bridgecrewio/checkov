from __future__ import annotations

import json
import os
import logging
from collections.abc import Iterable
from typing import TYPE_CHECKING, Any, cast

import yaml

from checkov.common.output.report import Report
from checkov.github_actions.image_referencer.manager import GithubActionsImageReferencerManager

from checkov.runner_filter import RunnerFilter
from jsonschema import validate, ValidationError

import checkov.common.parsers.yaml.loader as loader
from checkov.common.images.image_referencer import Image, ImageReferencerMixin
from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.util.consts import START_LINE, END_LINE
from checkov.common.util.type_forcers import force_dict
from checkov.github_actions.checks.registry import registry
from checkov.github_actions.schemas import gha_schema, gha_workflow
from checkov.yaml_doc.runner import Runner as YamlRunner

if TYPE_CHECKING:
    from checkov.common.checks.base_check_registry import BaseCheckRegistry
    from networkx import DiGraph

WORKFLOW_DIRECTORY = ".github/workflows/"


class Runner(ImageReferencerMixin["dict[str, dict[str, Any] | list[dict[str, Any]]]"], YamlRunner):
    check_type = CheckType.GITHUB_ACTIONS  # noqa: CCE003  # a static attribute

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
            entity_schema: tuple[dict[str, Any] | list[dict[str, Any]], list[tuple[int, str]]] | None = super()._parse_file(f)
            if not file_content:
                with open(f, 'r') as f_obj:
                    file_content = f_obj.read()
            if entity_schema and \
                    Runner.is_schema_valid(yaml.load(file_content, Loader=loader.SafeLineLoaderGhaSchema)):  # nosec
                return entity_schema
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
                graph_connector=None,
                root_path=root_folder,
                runner_filter=runner_filter,
                definitions=self.definitions,
                definitions_raw=self.definitions_raw
            )

            if image_report:
                if isinstance(report, list):
                    return [*report, image_report]
                return [report, image_report]

        return report

    def extract_images(
        self, graph_connector: DiGraph | None = None,
            definitions: dict[str, dict[str, Any] | list[dict[str, Any]]] | None = None,
            definitions_raw: dict[str, list[tuple[int, str]]] | None = None
    ) -> list[Image]:
        images: list[Image] = []
        if not definitions or not definitions_raw:
            return images

        for file, config in definitions.items():
            _config = force_dict(config) or {}
            manager = GithubActionsImageReferencerManager(workflow_config=_config, file_path=file,
                                                          workflow_line_numbers=definitions_raw[file])
            images.extend(manager.extract_images_from_workflow())

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
        for step in [step for step in job_definition.get('steps', []) or [] if step]:
            if step[START_LINE] <= start_line <= end_line <= step[END_LINE]:
                try:
                    name = step["name"]
                except KeyError:
                    name = step[next(iter(step.keys()))]

                return cast(str, name)

        return ""

    @staticmethod
    def is_schema_valid(config: dict[str, Any] | list[dict[str, Any]]) -> bool:
        valid = False
        config_dict = force_dict(config)
        try:
            validate(config_dict, gha_workflow)
            valid = True
        except ValidationError:
            try:
                validate(config_dict, gha_schema)
                valid = True
            except ValidationError:
                logging.info(f'Given entity configuration does not match the schema\n'
                             f'config={json.dumps(config_dict, indent=4)}\n')

        return valid
