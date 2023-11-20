from __future__ import annotations

import logging
import os
from collections.abc import Iterable
from typing import TYPE_CHECKING, Any, cast

from typing_extensions import TypeAlias  # noqa[TC002]

from checkov.arm.graph_builder.local_graph import ArmLocalGraph
from checkov.arm.graph_manager import ArmGraphManager
from checkov.arm.registry import arm_resource_registry, arm_parameter_registry
from checkov.arm.utils import get_scannable_file_paths, get_files_definitions, ARM_POSSIBLE_ENDINGS, ArmElements
from checkov.common.checks_infra.registry import get_graph_checks_registry
from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.graph.graph_builder.consts import GraphSource
from checkov.common.output.extra_resource import ExtraResource
from checkov.common.output.record import Record
from checkov.common.output.report import Report
from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.runners.base_runner import BaseRunner
from checkov.common.util.consts import START_LINE, END_LINE
from checkov.common.util.secrets import omit_secret_value_from_checks
from checkov.runner_filter import RunnerFilter
from checkov.arm.context_parser import ContextParser

if TYPE_CHECKING:
    from checkov.common.checks.base_check import BaseCheck
    from checkov.common.graph.checks_infra.base_check import BaseGraphCheck
    from checkov.common.graph.checks_infra.registry import BaseRegistry
    from checkov.common.typing import LibraryGraphConnector, _CheckResult

_ArmContext: TypeAlias = "dict[str, dict[str, Any]]"
_ArmDefinitions: TypeAlias = "dict[str, dict[str, Any]]"


class Runner(BaseRunner[_ArmDefinitions, _ArmContext, ArmGraphManager]):
    check_type = CheckType.ARM  # noqa: CCE003  # a static attribute

    def __init__(
        self,
        db_connector: LibraryGraphConnector | None = None,
        source: str = GraphSource.ARM,
        graph_class: type[ArmLocalGraph] = ArmLocalGraph,
        graph_manager: ArmGraphManager | None = None,
        external_registries: list[BaseRegistry] | None = None,
    ) -> None:
        super().__init__(file_extensions=ARM_POSSIBLE_ENDINGS)

        db_connector = db_connector or self.db_connector
        self.external_registries = external_registries if external_registries else []
        self.graph_class = graph_class
        self.graph_manager: "ArmGraphManager" = (
            graph_manager if graph_manager else ArmGraphManager(source=source, db_connector=db_connector)
        )
        self.graph_registry = get_graph_checks_registry(self.check_type)

        # need to check, how to support subclass differences
        self.definitions: _ArmDefinitions = {}
        self.definitions_raw: "dict[str, list[tuple[int, str]]]" = {}
        self.context: _ArmContext | None = None
        self.root_folder: "str | None" = None

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
        files_list: "Iterable[str]" = []
        filepath_fn = None
        if external_checks_dir:
            for directory in external_checks_dir:
                arm_resource_registry.load_external_checks(directory)

                if self.graph_registry:
                    self.graph_registry.load_external_checks(directory)

        if files:
            files_list = files.copy()

        if root_folder:
            filepath_fn = lambda f: f"/{os.path.relpath(f, os.path.commonprefix((root_folder, f)))}"
            self.root_folder = root_folder

            files_list = get_scannable_file_paths(root_folder=root_folder, excluded_paths=runner_filter.excluded_paths)

        self.definitions, self.definitions_raw, parsing_errors = get_files_definitions(files_list, filepath_fn)

        report.add_parsing_errors(parsing_errors)

        if self.graph_registry and self.graph_manager:
            logging.info("Creating ARM graph")
            local_graph = self.graph_manager.build_graph_from_definitions(definitions=self.definitions)
            logging.info("Successfully created ARM graph")

            self.graph_manager.save_graph(local_graph)

        self.pbar.initiate(len(self.definitions))

        # run Python checks
        self.add_python_check_results(report=report, runner_filter=runner_filter, root_folder=root_folder)

        # run graph checks
        if self.graph_registry:
            self.add_graph_check_results(report=report, runner_filter=runner_filter)

        return report

    def add_python_check_results(self, report: Report, runner_filter: RunnerFilter, root_folder: str | None) -> None:
        """Adds Python check results to given report"""

        for arm_file in self.definitions.keys():
            self.pbar.set_additional_data({"Current File Scanned": os.path.relpath(arm_file, root_folder)})
            # There are a few cases here. If -f was used, there could be a leading / because it's an absolute path,
            # or there will be no leading slash; root_folder will always be none.
            # If -d is used, root_folder will be the value given, and -f will start with a / (hardcoded above).
            # The goal here is simply to get a valid path to the file (which arm_file does not always give).
            if arm_file[0] == "/":
                path_to_convert = (root_folder + arm_file) if root_folder else arm_file
            else:
                path_to_convert = (os.path.join(root_folder, arm_file)) if root_folder else arm_file

            file_abs_path = os.path.abspath(path_to_convert)

            if isinstance(self.definitions[arm_file], dict):
                arm_context_parser = ContextParser(arm_file, self.definitions[arm_file], self.definitions_raw[arm_file])
                logging.debug(f"Template Dump for {arm_file}: {self.definitions[arm_file]}")

                if ArmElements.RESOURCES in self.definitions[arm_file]:
                    arm_context_parser.evaluate_default_parameters()

                    # Split out nested resources from base resource
                    for resource in self.definitions[arm_file][ArmElements.RESOURCES]:
                        if isinstance(resource, dict) and "parent_name" in resource.keys():
                            continue
                        nested_resources = arm_context_parser.search_deep_keys(ArmElements.RESOURCES, resource, [])
                        if nested_resources:
                            for nr in nested_resources:
                                nr_element = nr.pop()
                                if nr_element:
                                    for element in nr_element:
                                        new_resource = element
                                        if isinstance(new_resource, dict):
                                            new_resource["parent_name"] = resource.get("name", "")
                                            new_resource["parent_type"] = resource.get("type", "")
                                            self.definitions[arm_file][ArmElements.RESOURCES].append(new_resource)

                    for resource in self.definitions[arm_file][ArmElements.RESOURCES]:
                        resource_id = arm_context_parser.extract_arm_resource_id(resource)
                        resource_name = arm_context_parser.extract_arm_resource_name(resource)
                        if resource_id is None or resource_name is None:
                            logging.debug(f"Could not determine 'resource_id' of Resource {resource}")
                            continue

                        report.add_resource(f"{arm_file}:{resource_id}")
                        entity_lines_range, entity_code_lines = arm_context_parser.extract_arm_resource_code_lines(
                            resource
                        )
                        if entity_lines_range and entity_code_lines:
                            # TODO - Variable Eval Message!
                            variable_evaluations: "dict[str, Any]" = {}

                            skipped_checks = ContextParser.collect_skip_comments(resource)

                            results = arm_resource_registry.scan(
                                arm_file,
                                {resource_name: resource},
                                skipped_checks,
                                runner_filter,
                                report_type=CheckType.ARM,
                            )

                            if results:
                                for check, check_result in results.items():
                                    record = Record(
                                        check_id=check.id,
                                        bc_check_id=check.bc_id,
                                        check_name=check.name,
                                        check_result=check_result,
                                        code_block=entity_code_lines,
                                        file_path=arm_file,
                                        file_line_range=entity_lines_range,
                                        resource=resource_id,
                                        evaluations=variable_evaluations,
                                        check_class=check.__class__.__module__,
                                        file_abs_path=file_abs_path,
                                        severity=check.severity,
                                    )
                                    record.set_guideline(check.guideline)
                                    report.add_record(record=record)
                            else:
                                # resources without checks, but not existing ones
                                report.extra_resources.add(
                                    ExtraResource(
                                        file_abs_path=file_abs_path,
                                        file_path=arm_file,
                                        resource=resource_id,
                                    )
                                )

                if ArmElements.PARAMETERS in self.definitions[arm_file]:
                    parameters = self.definitions[arm_file][ArmElements.PARAMETERS]
                    for parameter_name, parameter_details in parameters.items():
                        # TODO - Variable Eval Message!
                        variable_evaluations = {}

                        resource_id = f"parameter.{parameter_name}"
                        resource_name = cast(str, parameter_name)
                        entity_lines_range, entity_code_lines = arm_context_parser.extract_arm_resource_code_lines(
                            parameter_details
                        )

                        if entity_lines_range and entity_code_lines:
                            skipped_checks = ContextParser.collect_skip_comments(parameter_details)
                            results = arm_parameter_registry.scan(
                                arm_file, {resource_name: parameter_details}, skipped_checks, runner_filter
                            )
                            for check, check_result in results.items():
                                censored_code_lines = omit_secret_value_from_checks(
                                    check=check,
                                    check_result=check_result,
                                    entity_code_lines=entity_code_lines,
                                    entity_config=parameter_details,
                                    resource_attributes_to_omit=runner_filter.resource_attr_to_omit,
                                )
                                self.build_record(
                                    report=report,
                                    check=check,
                                    check_result=check_result,
                                    code_block=censored_code_lines,
                                    file_path=arm_file,
                                    file_abs_path=file_abs_path,
                                    file_line_range=entity_lines_range,
                                    resource_id=resource_id,
                                    evaluations=variable_evaluations,
                                )

            self.pbar.update()
        self.pbar.close()

    def add_graph_check_results(self, report: Report, runner_filter: RunnerFilter) -> None:
        """Adds graph check results to given report"""

        graph_checks_results = self.run_graph_checks_results(runner_filter, self.check_type)

        for check, check_results in graph_checks_results.items():
            for check_result in check_results:
                entity = check_result["entity"]
                entity_file_path: str = entity[CustomAttributes.FILE_PATH]
                start_line = entity[START_LINE] - 1
                end_line = entity[END_LINE] - 1

                self.build_record(
                    report=report,
                    check=check,
                    check_result=check_result,
                    code_block=self.definitions_raw[entity_file_path][start_line:end_line],
                    file_path=entity_file_path,
                    file_abs_path=os.path.abspath(entity_file_path),
                    file_line_range=[start_line - 1, end_line - 1],
                    resource_id=entity[CustomAttributes.ID],
                )

    def build_record(
        self,
        report: Report,
        check: BaseCheck | BaseGraphCheck,
        check_result: _CheckResult,
        code_block: list[tuple[int, str]],
        file_path: str,
        file_abs_path: str,
        file_line_range: list[int],
        resource_id: str,
        evaluations: dict[str, Any] | None = None,
    ) -> None:
        record = Record(
            check_id=check.id,
            bc_check_id=check.bc_id,
            check_name=check.name,
            check_result=check_result,
            code_block=code_block,
            file_path=file_path,
            file_line_range=file_line_range,
            resource=resource_id,
            evaluations=evaluations,
            check_class=check.__class__.__module__,
            file_abs_path=file_abs_path,
            severity=check.severity,
        )
        record.set_guideline(check.guideline)
        report.add_record(record=record)
