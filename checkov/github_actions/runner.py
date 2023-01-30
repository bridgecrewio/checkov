from __future__ import annotations

import logging
import os
from collections.abc import Iterable
from typing import TYPE_CHECKING, Any

import yaml

from checkov.common.graph.graph_builder.consts import GraphSource
from checkov.common.output.report import Report
from checkov.github_actions.image_referencer.manager import GithubActionsImageReferencerManager
from checkov.github_actions.graph_builder.local_graph import GitHubActionsLocalGraph
from checkov.github_actions.utils import is_schema_valid, is_workflow_file

from checkov.runner_filter import RunnerFilter

import checkov.common.parsers.yaml.loader as loader
from checkov.common.images.image_referencer import Image, ImageReferencerMixin
from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.util.type_forcers import force_dict
from checkov.github_actions.checks.registry import registry
from checkov.yaml_doc.runner import Runner as YamlRunner

if TYPE_CHECKING:
    from checkov.common.checks.base_check_registry import BaseCheckRegistry
    from checkov.common.typing import LibraryGraphConnector
    from checkov.common.runners.graph_builder.local_graph import ObjectLocalGraph
    from checkov.common.runners.graph_manager import ObjectGraphManager
    from networkx import DiGraph


class Runner(ImageReferencerMixin["dict[str, dict[str, Any] | list[dict[str, Any]]]"], YamlRunner):
    check_type = CheckType.GITHUB_ACTIONS  # noqa: CCE003  # a static attribute

    def __init__(
        self,
        db_connector: LibraryGraphConnector | None = None,
        source: str = GraphSource.GITHUB_ACTIONS,
        graph_class: type[ObjectLocalGraph] = GitHubActionsLocalGraph,
        graph_manager: ObjectGraphManager | None = None,
        external_registries: dict[str, Any] | None = None
    ) -> None:
        super().__init__(
            db_connector=db_connector,
            source=source,
            graph_class=graph_class,
            graph_manager=graph_manager,
        )

    def require_external_checks(self) -> bool:
        return False

    def import_registry(self) -> BaseCheckRegistry:
        return registry

    def _parse_file(self, f: str, file_content: str | None = None) -> \
            tuple[dict[str, Any] | list[dict[str, Any]], list[tuple[int, str]]] | None:
        if is_workflow_file(f):
            entity_schema: tuple[dict[str, Any] | list[dict[str, Any]], list[tuple[int, str]]] | None = super()._parse_file(f)
            if not file_content:
                with open(f, 'r') as f_obj:
                    file_content = f_obj.read()
            if entity_schema and all(map(is_schema_valid, yaml.load_all(file_content, Loader=loader.SafeLineLoaderGhaSchema))):  # nosec
                return entity_schema
        return None

    def included_paths(self) -> Iterable[str]:
        return [".github"]

    def get_resource(self, file_path: str, key: str, supported_entities: Iterable[str],
                     start_line: int = -1, end_line: int = -1) -> str:
        """
        supported resources for GHA:
            jobs
            jobs.*.steps[]
            permissions
            on

        """
        if len(list(supported_entities)) > 1:
            logging.debug("order of entities might cause extracting the wrong key for resource_id")
        new_key = key
        definition = self.definitions.get(file_path, {})
        if not definition or not isinstance(definition, dict):
            return new_key
        if 'on' in supported_entities:
            workflow_name = definition.get('name', "")
            new_key = f"on({workflow_name})" if workflow_name else "on"
        elif 'jobs' in supported_entities:
            job_name = self.resolve_sub_name(definition, start_line, end_line, tag='jobs')
            new_key = f"jobs({job_name})" if job_name else "jobs"

            if 'jobs.*.steps[]' in supported_entities and key.split('.')[1] == '*':
                step_name = self.resolve_step_name(definition['jobs'].get(job_name), start_line, end_line)
                new_key = f'jobs({job_name}).steps{step_name}'
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

    def populate_metadata_dict(self) -> None:
        if isinstance(self.definitions, dict):
            # populate gha metadata dict
            for key, definition in self.definitions.items():
                if isinstance(definition, dict):
                    workflow_name = definition.get('name', '')
                    triggers = self._get_triggers(definition)
                    jobs = self._get_jobs(definition)
                    self.map_file_path_to_gha_metadata_dict[key] = {"triggers": triggers,
                                                                    "workflow_name": workflow_name, "jobs": jobs}
