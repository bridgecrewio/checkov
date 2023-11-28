from __future__ import annotations

import logging
import os
import platform

from abc import abstractmethod
from collections.abc import Iterable
from pathlib import Path
from typing import Any, TYPE_CHECKING, Callable, TypedDict
from typing_extensions import TypeAlias  # noqa[TC002]

from checkov.common.checks_infra.registry import get_graph_checks_registry
from checkov.common.models.enums import CheckResult
from checkov.common.typing import LibraryGraphConnector
from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.output.github_actions_record import GithubActionsRecord
from checkov.common.output.record import Record
from checkov.common.output.report import Report, CheckType
from checkov.common.parallelizer.parallel_runner import parallel_runner
from checkov.common.runners.base_runner import BaseRunner, filter_ignored_paths
from checkov.common.runners.graph_manager import ObjectGraphManager
from checkov.common.typing import _CheckResult
from checkov.common.util.consts import START_LINE, END_LINE
from checkov.runner_filter import RunnerFilter
from checkov.common.util.suppression import collect_suppressions_for_context

if TYPE_CHECKING:
    from checkov.common.checks.base_check_registry import BaseCheckRegistry
    from checkov.common.graph.checks_infra.base_check import BaseGraphCheck
    from checkov.common.runners.graph_builder.local_graph import ObjectLocalGraph

_ObjectContext: TypeAlias = "dict[str, dict[str, Any]]"
_ObjectDefinitions: TypeAlias = "dict[str, dict[str, Any] | list[dict[str, Any]]]"


class GhaMetadata(TypedDict):
    triggers: set[str]
    workflow_name: str
    jobs: dict[int, str]


class Runner(BaseRunner[_ObjectDefinitions, _ObjectContext, ObjectGraphManager]):
    def __init__(
        self,
        db_connector: LibraryGraphConnector | None = None,
        source: str | None = None,
        graph_class: type[ObjectLocalGraph] | None = None,
        graph_manager: ObjectGraphManager | None = None,
    ) -> None:
        super().__init__()
        self.definitions: _ObjectDefinitions = {}
        self.definitions_raw: dict[str, list[tuple[int, str]]] = {}
        self.context: _ObjectContext | None = None
        self.map_file_path_to_gha_metadata_dict: dict[str, GhaMetadata] = {}
        self.root_folder: str | None = None

        if source and graph_class:
            # if they are not all set, then ignore it
            db_connector = db_connector or self.db_connector
            self.source = source
            self.graph_class = graph_class
            self.graph_manager = (
                graph_manager if graph_manager else ObjectGraphManager(source=self.source, db_connector=db_connector)
            )
            self.graph_registry = get_graph_checks_registry(self.check_type)

    def _load_files(
            self,
            files_to_load: list[str],
            filename_fn: Callable[[str], str] | None = None,
    ) -> None:
        files_to_load = [filename_fn(file) if filename_fn else file for file in files_to_load]
        results = parallel_runner.run_function(lambda f: (f, self._parse_file(f)), files_to_load)
        for file_result_pair in results:
            if file_result_pair is None:
                # this only happens, when an uncaught exception occurs
                continue

            file, result = file_result_pair
            if result:
                (self.definitions[file], self.definitions_raw[file]) = result
                definition = result[0]
                if self.check_type == CheckType.GITHUB_ACTIONS and isinstance(definition, dict):
                    workflow_name = definition.get('name', '')
                    triggers = self._get_triggers(definition)
                    jobs = self._get_jobs(definition)
                    self.map_file_path_to_gha_metadata_dict[file] = \
                        {"triggers": triggers, "workflow_name": workflow_name, "jobs": jobs}

    @staticmethod
    @abstractmethod
    def _parse_file(f: str) -> tuple[dict[str, Any] | list[dict[str, Any]], list[tuple[int, str]]] | None:
        raise Exception("parser should be imported by deriving class")

    def run(
            self,
            root_folder: str | None = None,
            external_checks_dir: list[str] | None = None,
            files: list[str] | None = None,
            runner_filter: RunnerFilter | None = None,
            collect_skip_comments: bool = True,
    ) -> Report | list[Report]:
        runner_filter = runner_filter or RunnerFilter()
        if not runner_filter.show_progress_bar:
            self.pbar.turn_off_progress_bar()

        registry = self.import_registry()

        report = Report(self.check_type)

        if not files and not root_folder:
            logging.debug("No resources to scan.")
            return report

        if not external_checks_dir and self.require_external_checks():
            logging.debug("The runner requires that external checks are defined.")
            return report
        if external_checks_dir:
            for directory in external_checks_dir:
                registry.load_external_checks(directory)

                if self.graph_registry:
                    self.graph_registry.load_external_checks(directory)

        if not self.context or not self.definitions:
            if files:
                self._load_files(files)

            if root_folder:
                self.root_folder = root_folder

                for root, d_names, f_names in os.walk(root_folder):
                    filter_ignored_paths(root, d_names, runner_filter.excluded_paths, self.included_paths())
                    filter_ignored_paths(root, f_names, runner_filter.excluded_paths, self.included_paths())
                    files_to_load = [os.path.join(root, f_name) for f_name in f_names]
                    self._load_files(files_to_load=files_to_load)

            self.context = self.build_definitions_context(definitions=self.definitions, definitions_raw=self.definitions_raw)

            if self.graph_registry and self.graph_manager:
                logging.info(f"Creating {self.source} graph")
                local_graph = self.graph_manager.build_graph_from_definitions(
                    definitions=self.definitions, graph_class=self.graph_class  # type:ignore[arg-type]  # the paths are just `str`
                )

                logging.info(f"Successfully created {self.source} graph")

                self.graph_manager.save_graph(local_graph)
        else:
            logging.info("Going to use existing graph")
            self.populate_metadata_dict()

        self.pbar.initiate(len(self.definitions))

        # run Python checks
        self.add_python_check_results(report=report, registry=registry, runner_filter=runner_filter, root_folder=root_folder)

        # run graph checks
        if self.graph_registry:
            self.add_graph_check_results(report=report, runner_filter=runner_filter)

        return report

    def add_python_check_results(
        self, report: Report, registry: BaseCheckRegistry, runner_filter: RunnerFilter, root_folder: str | Path | None
    ) -> None:
        """Adds Python check results to given report"""

        for file_path in self.definitions.keys():
            self.pbar.set_additional_data({'Current File Scanned': os.path.relpath(file_path, root_folder)})
            skipped_checks = collect_suppressions_for_context(self.definitions_raw[file_path])

            if registry.report_type == CheckType.GITLAB_CI:
                registry.definitions_raw = self.definitions_raw[file_path]
            results = registry.scan(file_path, self.definitions[file_path], skipped_checks, runner_filter)  # type:ignore[arg-type] # this is overridden in the subclass
            for key, result in results.items():
                result_config = result["results_configuration"]
                start = 0
                end = 0
                check = result.pop("check", None)  # use pop to remove Check class which is not serializable from
                if check is None:
                    continue

                # result record
                if result_config:
                    end, start = self.get_start_end_lines(end, result_config, start)
                    if start == -1 and end == -1:
                        logging.info(f"Skipping line in file path {file_path} in key {key}")
                        continue
                if platform.system() == "Windows":
                    root_folder = os.path.split(file_path)[0]

                if self.check_type == CheckType.GITHUB_ACTIONS:
                    record: "Record" = GithubActionsRecord(
                        check_id=check.id,
                        bc_check_id=check.bc_id,
                        check_name=check.name,
                        check_result=result,
                        code_block=self.definitions_raw[file_path][start - 1:end + 1],
                        file_path=f"/{os.path.relpath(file_path, root_folder)}",
                        file_line_range=[start, end + 1],
                        resource=self.get_resource(file_path, key, check.supported_entities, start, end),  # type:ignore[arg-type]  # key is str not BaseCheck
                        evaluations=None,
                        check_class=check.__class__.__module__,
                        file_abs_path=os.path.abspath(file_path),
                        entity_tags=None,
                        severity=check.severity,
                        job=self.map_file_path_to_gha_metadata_dict[file_path]["jobs"].get(end, ''),
                        triggers=self.map_file_path_to_gha_metadata_dict[file_path]["triggers"],
                        workflow_name=self.map_file_path_to_gha_metadata_dict[file_path]["workflow_name"]
                    )
                else:
                    record = Record(
                        check_id=check.id,
                        bc_check_id=check.bc_id,
                        check_name=check.name,
                        check_result=result,
                        code_block=self.definitions_raw[file_path][start - 1:end + 1],
                        file_path=f"/{os.path.relpath(file_path, root_folder)}",
                        file_line_range=[start, end + 1],
                        resource=self.get_resource(file_path, key, check.supported_entities, start, end),  # type:ignore[arg-type]  # key is str not BaseCheck
                        evaluations=None,
                        check_class=check.__class__.__module__,
                        file_abs_path=os.path.abspath(file_path),
                        entity_tags=None,
                        severity=check.severity,
                    )
                report.add_record(record)
            self.pbar.update()
        self.pbar.close()

    def add_graph_check_results(self, report: Report, runner_filter: RunnerFilter) -> None:
        """Adds graph check results to given report"""

        root_folder = self.root_folder
        graph_checks_results = self.run_graph_checks_results(runner_filter, self.check_type)

        for check, check_results in graph_checks_results.items():
            for check_result in check_results:
                entity = check_result["entity"]
                entity_file_path: str = entity[CustomAttributes.FILE_PATH]

                if platform.system() == "Windows":
                    root_folder = os.path.split(entity_file_path)[0]

                clean_check_result: _CheckResult = {
                    "result": check_result["result"],
                    "evaluated_keys": check_result["evaluated_keys"],
                }

                start_line = entity[START_LINE]
                end_line = entity[END_LINE]
                code_block = self.get_code_block(entity=entity)

                self.add_inline_suppression(check=check, entity=entity, check_result=clean_check_result)

                if self.check_type == CheckType.GITHUB_ACTIONS:
                    if entity.get(CustomAttributes.BLOCK_NAME) == 'permissions' and start_line == 0 and end_line == 0:
                        # reconstruct permissions start-end lines since we do not have that information during graph build
                        for line in self.definitions_raw[entity_file_path]:
                            if line and 'permissions' in line[1]:
                                start_line = line[0]
                                end_line = line[0]
                                break

                    entity[CustomAttributes.ID] = self.get_resource(entity_file_path, entity[CustomAttributes.ID],
                                                                    entity[CustomAttributes.RESOURCE_TYPE],
                                                                    start_line, end_line, graph_resource=True)
                    record: "Record" = GithubActionsRecord(
                        check_id=check.id,
                        bc_check_id=check.bc_id,
                        check_name=check.name,
                        check_result=clean_check_result,
                        code_block=code_block,
                        file_path=f"/{os.path.relpath(entity_file_path, root_folder)}",
                        file_line_range=[start_line, end_line + 1],
                        resource=entity[CustomAttributes.ID],
                        evaluations=None,
                        check_class=check.__class__.__module__,
                        file_abs_path=os.path.abspath(entity_file_path),
                        entity_tags=None,
                        severity=check.severity,
                        job=self.map_file_path_to_gha_metadata_dict[entity_file_path]["jobs"].get(end_line, ''),
                        triggers=self.map_file_path_to_gha_metadata_dict[entity_file_path]["triggers"],
                        workflow_name=self.map_file_path_to_gha_metadata_dict[entity_file_path]["workflow_name"]
                    )
                else:
                    record = Record(
                        check_id=check.id,
                        bc_check_id=check.bc_id,
                        check_name=check.name,
                        check_result=clean_check_result,
                        code_block=code_block,
                        file_path=f"/{os.path.relpath(entity_file_path, root_folder)}",
                        file_line_range=[start_line, end_line + 1],
                        resource=entity[CustomAttributes.ID],
                        evaluations=None,
                        check_class=check.__class__.__module__,
                        file_abs_path=os.path.abspath(entity_file_path),
                        entity_tags=None,
                        severity=check.severity,
                    )

                record.set_guideline(check.guideline)
                report.add_record(record=record)

    def get_resource(self, file_path: str, key: str, supported_entities: Iterable[str],
                     start_line: int = -1, end_line: int = -1, graph_resource: bool = False) -> str:
        return f"{file_path}.{key}"

    @abstractmethod
    def get_start_end_lines(self, end: int, result_config: dict[str, Any], start: int) -> tuple[int, int]:
        raise Exception("should be handled by derived class")

    @abstractmethod
    def import_registry(self) -> BaseCheckRegistry:
        raise Exception("registry should be imported by deriving class")

    def require_external_checks(self) -> bool:
        return True

    @staticmethod
    def _change_files_path_to_relative(report: Report) -> None:
        for record in report.get_all_records():
            record.file_path = record.file_path.replace(os.getcwd(), "")
            record.resource = record.resource.replace(os.getcwd(), "")

    def build_definitions_context(
        self,
        definitions: dict[str, dict[str, Any] | list[dict[str, Any]]],
        definitions_raw: dict[str, list[tuple[int, str]]],
    ) -> dict[str, dict[str, Any]]:
        # if needed, should be overridden in the actual runner class
        return {}

    def get_code_block(self, entity: dict[str, Any]) -> list[tuple[int, str]]:
        """Returns the code block either from context or definitions_raw"""

        code_block: list[tuple[int, str]] = []

        entity_file_path = entity[CustomAttributes.FILE_PATH]

        if self.context:
            # not all runners have the 'context' attribute populated
            entity_id = entity[CustomAttributes.ID]
            entity_context = self.context[entity_file_path].get(entity_id)

            if entity_context:
                code_block = entity_context.get("code_lines")
            else:
                logging.info(f"Could not find context for resource {entity_id} in file {entity_file_path}")

        if not code_block:
            # fallback, if context extraction failed
            start_line = entity[START_LINE]
            end_line = entity[END_LINE]
            code_block = self.definitions_raw[entity_file_path][start_line - 1:end_line + 1]

        return code_block

    def add_inline_suppression(self, check: BaseGraphCheck, entity: dict[str, Any], check_result: _CheckResult) -> None:
        """Adjusts check result, if inline suppressed"""

        if self.context:
            # not all runners have the 'context' attribute populated
            entity_file_path = entity[CustomAttributes.FILE_PATH]
            entity_id = entity[CustomAttributes.ID]
            entity_context = self.context[entity_file_path].get(entity_id)

            if entity_context:
                skipped_check = next(
                    (
                        skipped_check
                        for skipped_check in entity_context.get("skipped_checks", [])
                        if skipped_check["id"] in (check.id, check.bc_id)
                    ),
                    None,
                )
                if skipped_check:
                    check_result["result"] = CheckResult.SKIPPED
                    check_result["suppress_comment"] = skipped_check.get("suppress_comment", "")

    def _get_triggers(self, definition: dict[str, Any]) -> set[str]:
        triggers_set = set()
        triggers = definition.get("on")
        try:
            if isinstance(triggers, str):
                triggers_set.add(triggers)
            elif isinstance(triggers, dict):
                triggers_set = {key for key in triggers.keys() if key != START_LINE and key != END_LINE}

        except Exception as e:
            logging.info(f"failed to parse workflow triggers due to:{str(e)}")
        return triggers_set

    def _get_jobs(self, definition: dict[str, Any]) -> dict[int, str]:
        end_line_to_job_name_dict: dict[int, str] = {}
        jobs = definition.get('jobs')
        if jobs:
            for job_name, job_instance in jobs.items():
                if not isinstance(job_instance, dict):
                    continue
                if job_name != START_LINE and job_name != END_LINE:
                    end_line: int = job_instance.get(END_LINE, -1)
                    end_line_to_job_name_dict[end_line] = job_name

                    steps: list[dict[str, Any]] = [step for step in job_instance.get('steps', []) or [] if step]
                    if not steps:
                        continue

                    for step in steps:
                        if not isinstance(step, dict) or END_LINE not in step:
                            continue
                        end_line_to_job_name_dict[step.get(END_LINE)] = job_name  # type: ignore[index] #
        return end_line_to_job_name_dict
