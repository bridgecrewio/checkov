from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING, Any

from typing_extensions import TypeAlias  # noqa[TC002]

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.checks_infra.registry import get_graph_checks_registry
from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.graph.graph_builder.consts import GraphSource
from checkov.common.output.graph_record import GraphRecord
from checkov.common.output.record import Record
from checkov.common.output.report import Report
from checkov.common.resource_code_logger_filter import add_resource_code_filter_to_logger
from checkov.common.util.consts import START_LINE, END_LINE
from checkov.common.util.secrets import omit_secret_value_from_checks
from checkov.runner_filter import RunnerFilter
from checkov.terraform.base_runner import BaseTerraformRunner
from checkov.terraform.checks.resource.registry import resource_registry
from checkov.terraform.graph_builder.local_graph import TerraformLocalGraph
from checkov.terraform_json.utils import get_scannable_file_paths, create_definitions

if TYPE_CHECKING:
    from checkov.common.graph.checks_infra.registry import BaseRegistry
    from checkov.terraform.graph_manager import TerraformGraphManager
    from checkov.common.typing import LibraryGraphConnector, _CheckResult

_TerraformJsonContext: TypeAlias = "dict[str, dict[str, Any]]"
_TerraformJsonDefinitions: TypeAlias = "dict[str, dict[str, Any]]"

logger = logging.getLogger(__name__)
add_resource_code_filter_to_logger(logger)


class TerraformJsonRunner(BaseTerraformRunner[_TerraformJsonDefinitions, _TerraformJsonContext, str]):
    check_type = CheckType.TERRAFORM_JSON  # noqa: CCE003  # a static attribute

    def __init__(
        self,
        graph_class: type[TerraformLocalGraph] = TerraformLocalGraph,
        graph_manager: TerraformGraphManager | None = None,
        db_connector: LibraryGraphConnector | None = None,
        external_registries: list[BaseRegistry] | None = None,
        source: str = GraphSource.TERRAFORM,
    ) -> None:
        super().__init__(
            graph_class=graph_class,
            graph_manager=graph_manager,
            db_connector=db_connector,
            external_registries=external_registries,
            source=source,
        )
        self.file_extensions = (".json",)  # just '.json' not 'tf.json' otherwise it will be filtered out
        self.graph_registry = get_graph_checks_registry(check_type=CheckType.TERRAFORM)

        self.definitions: _TerraformJsonDefinitions = {}
        self.definitions_raw: "dict[str, list[tuple[int, str]]]" = {}
        self.context: _TerraformJsonContext = {}
        self.root_folder: str | None = None

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
        self.root_folder = root_folder

        if not self.definitions or not self.context:
            file_paths = get_scannable_file_paths(
                root_folder=root_folder, files=files, excluded_paths=runner_filter.excluded_paths
            )

            if not file_paths:
                return report

            self.definitions, self.definitions_raw, parsing_errors = create_definitions(file_paths)

            report.add_parsing_errors(parsing_errors)

            if external_checks_dir:
                for directory in external_checks_dir:
                    resource_registry.load_external_checks(directory)
                    self.graph_registry.load_external_checks(directory)

            # TODO: create function 'build_definitions_context()'
            # self.context = build_definitions_context(definitions=self.definitions, definitions_raw=self.definitions_raw)

            logger.info("Creating Terraform JSON graph")
            local_graph = self.graph_manager.build_graph_from_definitions(self.definitions)
            logger.info("Successfully created Terraform JSON graph")

            self.graph_manager.save_graph(local_graph)

            self.pbar.initiate(len(self.definitions))

            # run Python checks
            self.add_python_check_results(report=report, runner_filter=runner_filter)

            # run graph checks
            self.add_graph_check_results(report=report, runner_filter=runner_filter)

        return report

    def add_python_check_results(self, report: Report, runner_filter: RunnerFilter) -> None:
        """Adds Python check results to given report"""

        for full_file_path, definition in self.definitions.items():
            scanned_file = f"/{os.path.relpath(full_file_path, self.root_folder)}"
            logger.debug(f"Scanning file: {scanned_file}")
            self.pbar.set_additional_data({"Current File Scanned": scanned_file})
            for block_type in definition.keys():
                if block_type in self.block_type_registries:
                    self.run_block(
                        entities=definition[block_type],
                        definition_context={},
                        full_file_path=full_file_path,
                        root_folder=self.root_folder,
                        report=report,
                        scanned_file=scanned_file,
                        block_type=block_type,
                        runner_filter=runner_filter,
                    )

            self.pbar.update()
        self.pbar.close()

    def add_graph_check_results(self, report: Report, runner_filter: RunnerFilter) -> None:
        """Adds YAML check results to given report"""

        checks_results = self.run_graph_checks_results(
            runner_filter=runner_filter, report_type=CheckType.TERRAFORM_JSON
        )

        for check, check_results in checks_results.items():
            for check_result in check_results:
                entity = check_result["entity"]
                entity_file_path = entity[CustomAttributes.FILE_PATH]

                clean_check_result: "_CheckResult" = {
                    "result": check_result["result"],
                    "evaluated_keys": check_result["evaluated_keys"],
                }

                file_code_lines = self.definitions_raw[entity_file_path]
                start_line = entity[START_LINE]
                end_line = entity[END_LINE]
                scanned_file = f"/{os.path.relpath(entity_file_path, self.root_folder)}"

                record = Record(
                    check_id=check.id,
                    bc_check_id=check.bc_id,
                    check_name=check.name,
                    check_result=clean_check_result,
                    code_block=file_code_lines[start_line - 1 : end_line],
                    file_path=scanned_file,
                    file_line_range=[start_line, end_line],
                    resource=entity[CustomAttributes.ID],
                    check_class=check.__class__.__module__,
                    file_abs_path=str(entity_file_path),
                    evaluations=None,
                    severity=check.severity,
                )
                if self.breadcrumbs:
                    breadcrumb = self.breadcrumbs.get(record.file_path, {}).get(record.resource)
                    if breadcrumb:
                        record = GraphRecord(record, breadcrumb)
                record.set_guideline(guideline=check.guideline)
                report.add_record(record=record)

    def run_block(
        self,
        entities: list[dict[str, Any]],
        definition_context: _TerraformJsonContext,
        full_file_path: str,
        root_folder: str | None,
        report: Report,
        scanned_file: str,
        block_type: str,
        runner_filter: RunnerFilter | None = None,
        entity_context_path_header: str | None = None,
        module_referrer: str | None = None,
    ) -> None:
        """Run block specific checks"""

        runner_filter = runner_filter or RunnerFilter()
        registry = self.block_type_registries[block_type]
        if registry:
            for entity in entities:
                _, entity_name, entity_config = registry.extract_entity_details(entity)

                start_line = entity_config[START_LINE]
                end_line = entity_config[END_LINE]
                entity_id = f"{block_type}.{entity_name}"
                entity_lines_range = [start_line, end_line]
                entity_code_lines = self.definitions_raw[full_file_path][start_line - 1 : end_line]

                results = registry.scan(scanned_file, entity, [], runner_filter, report_type=CheckType.TERRAFORM_JSON)
                for check, check_result in results.items():
                    censored_code_lines = omit_secret_value_from_checks(
                        check=check,
                        check_result=check_result,
                        entity_code_lines=entity_code_lines,
                        entity_config=entity_config,
                        resource_attributes_to_omit=runner_filter.resource_attr_to_omit,
                    )
                    record = Record(
                        check_id=check.id,
                        bc_check_id=check.bc_id,
                        check_name=check.name,
                        check_result=check_result,
                        code_block=censored_code_lines,
                        file_path=scanned_file,
                        file_line_range=entity_lines_range,
                        resource=entity_id,
                        evaluations=None,
                        check_class=check.__class__.__module__,
                        file_abs_path=full_file_path,
                        severity=check.severity,
                        details=check.details,
                    )
                    record.set_guideline(guideline=check.guideline)
                    report.add_record(record=record)

    def get_entity_context_and_evaluations(self, entity: dict[str, Any]) -> dict[str, Any] | None:
        # not used
        pass
