from __future__ import annotations

import logging
import os
import platform

from abc import abstractmethod
from collections.abc import Iterable
from typing import Any, TYPE_CHECKING, Callable
from typing_extensions import TypedDict

from checkov.common.output.github_actions_record import GithubActionsRecord
from checkov.common.output.record import Record
from checkov.common.output.report import Report, CheckType
from checkov.common.parallelizer.parallel_runner import parallel_runner
from checkov.common.runners.base_runner import BaseRunner, filter_ignored_paths
from checkov.common.util.consts import START_LINE, END_LINE
from checkov.runner_filter import RunnerFilter
from checkov.common.util.suppression import collect_suppressions_for_context

if TYPE_CHECKING:
    from checkov.common.checks.base_check_registry import BaseCheckRegistry


class GhaMetadata(TypedDict):
    triggers: set[str]
    workflow_name: str
    jobs: dict[int, str]


class Runner(BaseRunner[None]):  # if a graph is added, Any needs to replaced
    def __init__(self) -> None:
        super().__init__()
        self.definitions: dict[str, dict[str, Any] | list[dict[str, Any]]] = {}
        self.definitions_raw: dict[str, list[tuple[int, str]]] = {}
        self.map_file_path_to_gha_metadata_dict: dict[str, GhaMetadata] = {}

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

    @abstractmethod
    def _parse_file(
            self, f: str
    ) -> tuple[dict[str, Any] | list[dict[str, Any]], list[tuple[int, str]]] | None:
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

        if files:
            self._load_files(files)

        if root_folder:
            for root, d_names, f_names in os.walk(root_folder):
                filter_ignored_paths(root, d_names, runner_filter.excluded_paths, self.included_paths())
                filter_ignored_paths(root, f_names, runner_filter.excluded_paths, self.included_paths())
                files_to_load = [os.path.join(root, f_name) for f_name in f_names]
                self._load_files(files_to_load=files_to_load)

        self.pbar.initiate(len(self.definitions))
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
                        resource=self.get_resource(file_path, key, check.supported_entities, self.definitions[file_path]),  # type:ignore[arg-type]  # key is str not BaseCheck
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
                        resource=self.get_resource(file_path, key, check.supported_entities),  # type:ignore[arg-type]  # key is str not BaseCheck
                        evaluations=None,
                        check_class=check.__class__.__module__,
                        file_abs_path=os.path.abspath(file_path),
                        entity_tags=None,
                        severity=check.severity,
                    )
                report.add_record(record)
            self.pbar.update()
        self.pbar.close()
        return report

    def included_paths(self) -> Iterable[str]:
        return []

    def get_resource(self, file_path: str, key: str, supported_entities: Iterable[str], definitions: dict[str, Any] | None = None) -> str:
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

                    steps = [step for step in job_instance.get('steps', []) or [] if step]
                    if steps:
                        for step in steps:
                            end_line_to_job_name_dict[step.get(END_LINE)] = job_name
        return end_line_to_job_name_dict
