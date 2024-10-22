from __future__ import annotations

import logging
import os
from collections.abc import Iterable
from typing import TYPE_CHECKING, Any

from typing_extensions import TypeAlias  # noqa[TC002]

from checkov.common.checks_infra.registry import get_graph_checks_registry
from checkov.common.models.enums import CheckResult
from checkov.common.typing import LibraryGraphConnector
from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.graph.graph_builder.consts import GraphSource
from checkov.common.images.image_referencer import ImageReferencerMixin
from checkov.common.output.record import Record
from checkov.common.output.report import Report
from checkov.common.output.extra_resource import ExtraResource
from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.runners.base_runner import BaseRunner
from checkov.common.util.consts import START_LINE, END_LINE
from checkov.common.util.dockerfile import is_dockerfile
from checkov.common.typing import _CheckResult
from checkov.dockerfile.graph_builder.local_graph import DockerfileLocalGraph
from checkov.dockerfile.graph_manager import DockerfileGraphManager
from checkov.dockerfile.image_referencer.manager import DockerfileImageReferencerManager
from checkov.dockerfile.parser import collect_skipped_checks
from checkov.dockerfile.registry import registry
from checkov.dockerfile.utils import (
    DOCKERFILE_STARTLINE,
    DOCKERFILE_ENDLINE,
    get_files_definitions,
    get_scannable_file_paths,
    get_abs_path,
    build_definitions_context,
)
from checkov.runner_filter import RunnerFilter

if TYPE_CHECKING:
    from dockerfile_parse.parser import _Instruction  # only in extra_stubs
    from networkx import DiGraph
    from checkov.common.checks.base_check import BaseCheck
    from checkov.common.graph.checks_infra.base_check import BaseGraphCheck
    from checkov.common.images.image_referencer import Image

_DockerfileContext: TypeAlias = "dict[str, dict[str, Any]]"
_DockerfileDefinitions: TypeAlias = "dict[str, dict[str, list[_Instruction]]]"


class Runner(ImageReferencerMixin[_DockerfileDefinitions], BaseRunner[_DockerfileDefinitions, _DockerfileContext, DockerfileGraphManager]):
    check_type = CheckType.DOCKERFILE  # noqa: CCE003  # a static attribute

    def __init__(
        self,
        db_connector: LibraryGraphConnector | None = None,
        source: str = GraphSource.DOCKERFILE,
        graph_class: type[DockerfileLocalGraph] = DockerfileLocalGraph,
        graph_manager: DockerfileGraphManager | None = None,
    ) -> None:

        super().__init__()
        db_connector = db_connector or self.db_connector
        self.graph_class = graph_class
        self.graph_manager = (
            graph_manager if graph_manager else DockerfileGraphManager(source=source, db_connector=db_connector)
        )
        self.graph_registry = get_graph_checks_registry(self.check_type)

        self.context: _DockerfileContext = {}
        self.definitions: _DockerfileDefinitions = {}
        self.definitions_raw: "dict[str, list[str]]" = {}       # type:ignore[assignment]
        self.root_folder: str | None = None

    def should_scan_file(self, filename: str) -> bool:
        return is_dockerfile(os.path.basename(filename))

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

        report = Report(self.check_type)

        if not self.context or not self.definitions:
            files_list: "Iterable[str]" = []
            filepath_fn = None
            if external_checks_dir:
                for directory in external_checks_dir:
                    registry.load_external_checks(directory)

                    if self.graph_registry:
                        self.graph_registry.load_external_checks(directory)

            if files:
                files_list = [file for file in files if is_dockerfile(os.path.basename(file))]

            if root_folder:
                filepath_fn = lambda f: f"/{os.path.relpath(f, os.path.commonprefix((root_folder, f)))}"
                self.root_folder = root_folder

                files_list = get_scannable_file_paths(root_folder=root_folder, excluded_paths=runner_filter.excluded_paths)

            self.definitions, self.definitions_raw = get_files_definitions(files_list, filepath_fn)

            self.context = build_definitions_context(definitions=self.definitions, definitions_raw=self.definitions_raw)

            if self.graph_registry and self.graph_manager:
                logging.info("Creating Dockerfile graph")
                local_graph = self.graph_manager.build_graph_from_definitions(definitions=self.definitions)
                logging.info("Successfully created Dockerfile graph")

                self.graph_manager.save_graph(local_graph)

        self.pbar.initiate(len(self.definitions))

        # run Python checks
        self.add_python_check_results(report=report, runner_filter=runner_filter, root_folder=root_folder)

        # run graph checks
        if self.graph_registry:
            self.add_graph_check_results(report=report, runner_filter=runner_filter, root_folder=root_folder)

        if runner_filter.run_image_referencer:
            if files:
                # 'root_folder' shouldn't be empty to remove the whole path later and only leave the shortened form
                root_folder = os.path.split(os.path.commonprefix(files))[0]

            image_report = self.check_container_image_references(
                root_path=root_folder,
                runner_filter=runner_filter,
                definitions=self.definitions,
            )

            if image_report:
                # due too many tests failing only return a list, if there is an image report
                return [report, image_report]

        return report

    def add_python_check_results(self, report: Report, runner_filter: RunnerFilter, root_folder: str | None) -> None:
        """Adds Python check results to given report"""

        for dockerfile_path, instructions in self.definitions.items():
            self.pbar.set_additional_data({"Current File Scanned": os.path.relpath(dockerfile_path, root_folder)})

            file_abs_path = get_abs_path(root_folder=root_folder, file_path=dockerfile_path)
            report.add_resource(file_abs_path)
            skipped_checks = collect_skipped_checks(instructions)

            results = registry.scan(dockerfile_path, instructions, skipped_checks, runner_filter)

            if results:
                for check, check_result in results.items():
                    result_configuration = check_result["results_configuration"]
                    startline = 0
                    endline = len(self.definitions_raw[dockerfile_path]) - 1
                    result_instruction = ""
                    if result_configuration:
                        if isinstance(result_configuration, list):
                            for res in result_configuration:
                                startline = res[DOCKERFILE_STARTLINE]
                                endline = res[DOCKERFILE_ENDLINE]
                                result_instruction = res["instruction"]
                                self.build_record(
                                    report,
                                    self.definitions_raw,
                                    dockerfile_path,
                                    file_abs_path,
                                    check,
                                    check_result,
                                    startline,
                                    endline,
                                    result_instruction,
                                )
                        else:
                            startline = result_configuration[DOCKERFILE_STARTLINE]
                            endline = result_configuration[DOCKERFILE_ENDLINE]
                            result_instruction = result_configuration["instruction"]
                            self.build_record(
                                report,
                                self.definitions_raw,
                                dockerfile_path,
                                file_abs_path,
                                check,
                                check_result,
                                startline,
                                endline,
                                result_instruction,
                            )
                    else:
                        self.build_record(
                            report,
                            self.definitions_raw,
                            dockerfile_path,
                            file_abs_path,
                            check,
                            check_result,
                            startline,
                            endline,
                            result_instruction,
                        )
            else:
                report.extra_resources.add(
                    ExtraResource(
                        file_abs_path=file_abs_path,
                        file_path=dockerfile_path,
                        resource=dockerfile_path,
                    )
                )

            self.pbar.update()
        self.pbar.close()

    def add_graph_check_results(self, report: Report, runner_filter: RunnerFilter, root_folder: str | None) -> None:
        """Adds graph check results to given report"""

        graph_checks_results = self.run_graph_checks_results(runner_filter, self.check_type)

        for check, check_results in graph_checks_results.items():
            for check_result in check_results:
                entity = check_result["entity"]
                entity_file_path: str = entity[CustomAttributes.FILE_PATH]
                file_abs_path = get_abs_path(root_folder=root_folder, file_path=entity_file_path)
                resource_type: str = entity[CustomAttributes.RESOURCE_TYPE]
                start_line = entity[START_LINE]
                end_line = entity[END_LINE]

                self.build_record(
                    report=report,
                    definitions_raw=self.definitions_raw,
                    dockerfile_path=entity_file_path,
                    file_abs_path=file_abs_path,
                    check=check,
                    check_result=check_result,
                    startline=start_line,
                    endline=end_line,
                    result_instruction=resource_type,
                )

    def calc_record_codeblock(
        self,
        codeblock: list[tuple[int, str]],
        definitions_raw: dict[str, list[str]],
        dockerfile_path: str,
        endline: int,
        startline: int,
    ) -> None:
        for line in range(startline, endline + 1):
            codeblock.append((line + 1, definitions_raw[dockerfile_path][line]))

    def build_record(
        self,
        report: Report,
        definitions_raw: dict[str, list[str]],
        dockerfile_path: str,
        file_abs_path: str,
        check: BaseCheck | BaseGraphCheck,
        check_result: _CheckResult,
        startline: int,
        endline: int,
        result_instruction: str,
    ) -> None:
        codeblock: list[tuple[int, str]] = []

        if result_instruction:
            entity_context = next(
                (
                    resource
                    for resource in self.context[dockerfile_path][result_instruction]
                    if resource["start_line"] == startline + 1
                ),
                None,
            )
            if entity_context:
                codeblock = entity_context["code_lines"]
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
            else:
                logging.info(f"Could not find context for resource with start line {startline + 1} in {self.context[dockerfile_path][result_instruction]}")
        else:
            self.calc_record_codeblock(codeblock, definitions_raw, dockerfile_path, endline, startline)

        record = Record(
            check_id=check.id,
            bc_check_id=check.bc_id,
            check_name=check.name,
            check_result=check_result,
            code_block=codeblock,
            file_path=dockerfile_path,
            file_line_range=[startline + 1, endline + 1],
            resource=f"{dockerfile_path}.{result_instruction}",
            evaluations=None,
            check_class=check.__class__.__module__,
            file_abs_path=file_abs_path,
            entity_tags=None,
            severity=check.severity,
        )
        record.set_guideline(check.guideline)
        report.add_record(record=record)

    def extract_images(
        self,
        graph_connector: DiGraph | None = None,
        definitions: dict[str, dict[str, list[_Instruction]]] | None = None,
        definitions_raw: dict[str, list[tuple[int, str]]] | None = None,
    ) -> list[Image]:
        if not definitions:
            # should not happen
            return []

        manager = DockerfileImageReferencerManager(definitions=definitions)
        images = manager.extract_images_from_resources()

        return images
