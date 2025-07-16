from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any
from typing_extensions import TypeAlias  # noqa[TC002]

from checkov.cloudformation import cfn_utils
from checkov.cloudformation.context_parser import ContextParser as CfnContextParser
from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.util.secrets import omit_secret_value_from_checks
from checkov.serverless.base_registry import EntityDetails
from checkov.serverless.graph_builder.definition_context import build_definitions_context
from checkov.serverless.graph_builder.graph_to_definitions import convert_graph_vertices_to_definitions
from checkov.serverless.graph_builder.local_graph import ServerlessLocalGraph
from checkov.serverless.graph_manager import ServerlessGraphManager
from checkov.serverless.parsers.context_parser import ContextParser as SlsContextParser, ContextParser
from checkov.cloudformation.checks.resource.registry import cfn_registry
from checkov.serverless.checks.complete.registry import complete_registry
from checkov.serverless.checks.custom.registry import custom_registry
from checkov.serverless.checks.function.registry import function_registry
from checkov.serverless.checks.layer.registry import layer_registry
from checkov.serverless.checks.package.registry import package_registry
from checkov.serverless.checks.plugin.registry import plugin_registry
from checkov.serverless.checks.provider.registry import provider_registry
from checkov.serverless.checks.service.registry import service_registry
from checkov.common.runners.base_runner import BaseRunner
from checkov.runner_filter import RunnerFilter
from checkov.common.checks_infra.registry import get_graph_checks_registry
from checkov.common.output.record import Record
from checkov.common.output.report import Report
from checkov.common.graph.graph_builder.consts import GraphSource
from checkov.common.output.extra_resource import ExtraResource
from checkov.serverless.parsers.parser import CFN_RESOURCES_TOKEN
from checkov.serverless.utils import get_scannable_file_paths, get_files_definitions, SLS_FILE_MASK, get_resource_tags

if TYPE_CHECKING:
    from checkov.common.graph.checks_infra.registry import BaseRegistry
    from checkov.common.typing import LibraryGraphConnector

MULTI_ITEM_SECTIONS = [
    ("functions", function_registry),
    ("layers", layer_registry)
]
SINGLE_ITEM_SECTIONS = [
    ("provider", provider_registry),
    ("custom", custom_registry),
    ("package", package_registry),
    ("plugins", plugin_registry),
    ("service", service_registry)
]

_ServerlessContext: TypeAlias = "dict[str, dict[str, Any]]"
_ServerlessDefinitions: TypeAlias = "dict[str, dict[str, Any]]"


class Runner(BaseRunner[_ServerlessDefinitions, _ServerlessContext, ServerlessGraphManager]):
    check_type = CheckType.SERVERLESS  # noqa: CCE003  # a static attribute

    def __init__(self,
                 db_connector: LibraryGraphConnector | None = None,
                 source: str = GraphSource.SERVERLESS,
                 graph_class: type[ServerlessLocalGraph] = ServerlessLocalGraph,
                 graph_manager: ServerlessGraphManager | None = None,
                 external_registries: list[BaseRegistry] | None = None,
                 ) -> None:
        super().__init__(file_names=SLS_FILE_MASK)

        db_connector = db_connector or self.db_connector
        self.external_registries = external_registries if external_registries else []
        self.graph_class = graph_class
        self.graph_manager: "ServerlessGraphManager" = (
            graph_manager if graph_manager else ServerlessGraphManager(source=source, db_connector=db_connector)
        )
        self.graph_registry = get_graph_checks_registry(self.check_type)

        self.definitions: _ServerlessDefinitions = {}
        self.definitions_raw: dict[str, list[tuple[int, str]]] = {}
        self.context: _ServerlessContext | None = None
        self.root_folder: "str | None" = None

    def run(
            self,
            root_folder: str | None,
            external_checks_dir: list[str] | None = None,
            files: list[str] | None = None,
            runner_filter: RunnerFilter | None = None,
            collect_skip_comments: bool = True,
    ) -> Report:
        runner_filter = runner_filter or RunnerFilter()
        if not runner_filter.show_progress_bar:
            self.pbar.turn_off_progress_bar()

        report = Report(self.check_type)
        self.root_folder = root_folder

        if not self.context or not self.definitions:
            files_list: list[str] = []
            filepath_fn = None
            if external_checks_dir:
                for directory in external_checks_dir:
                    function_registry.load_external_checks(directory)

            if files:
                files_list = [file for file in files if os.path.basename(file) in SLS_FILE_MASK]

            if self.root_folder:
                files_list = get_scannable_file_paths(self.root_folder, runner_filter.excluded_paths)

            definitions, definitions_raw = get_files_definitions(files_list, filepath_fn)

            # Filter out empty files that have not been parsed successfully
            self.definitions = {k: v for k, v in definitions.items() if v}
            self.definitions_raw = {k: v for k, v in definitions_raw.items() if k in definitions.keys()}
            self.context = build_definitions_context(definitions=self.definitions, definitions_raw=self.definitions_raw)

            logging.info("Creating Serverless graph")
            local_graph = self.graph_manager.build_graph_from_definitions(definitions=self.definitions)
            logging.info(f'Successfully created Serverless graph ({len(local_graph.vertices)} vertices)')

            self.graph_manager.save_graph(local_graph)
            self.definitions, self.breadcrumbs = convert_graph_vertices_to_definitions(
                vertices=local_graph.vertices,
                root_folder=root_folder,
            )

        self.pbar.initiate(len(self.definitions))

        self.add_python_check_results(report, runner_filter)

        return report

    def add_python_check_results(self, report: Report, runner_filter: RunnerFilter) -> None:
        for sls_file, sls_file_data in self.definitions.items():
            self.pbar.set_additional_data({'Current File Scanned': os.path.relpath(sls_file, self.root_folder)})
            if not isinstance(sls_file_data, dict):
                continue

            sls_context_parser = SlsContextParser(sls_file, sls_file_data, self.definitions_raw[sls_file])

            self.cfn_resources_checks(sls_file, sls_file_data, report, runner_filter)
            self.multi_item_sections_checks(sls_file, sls_file_data, report, runner_filter, sls_context_parser)
            self.single_item_sections_checks(sls_file, sls_file_data, report, runner_filter, sls_context_parser)
            self.complete_python_checks(sls_file, sls_file_data, report, runner_filter, sls_context_parser)

    def complete_python_checks(self,
                               sls_file: str,
                               sls_file_data: dict[str, Any],
                               report: Report,
                               runner_filter: RunnerFilter,
                               sls_context_parser: ContextParser) -> None:
        # "Complete" checks
        # NOTE: Ignore code content, no point in showing (could be long)
        file_abs_path = Path(sls_file).absolute()
        entity_code_lines = self.definitions_raw[sls_file]
        entity_lines_range = [1, len(entity_code_lines) - 1]
        skipped_checks = CfnContextParser.collect_skip_comments(entity_code_lines or [])
        variable_evaluations: dict[str, Any] = {}
        entity = EntityDetails(sls_context_parser.provider_type, sls_file_data)
        results = complete_registry.scan(sls_file, entity, skipped_checks, runner_filter)
        tags = cfn_utils.get_resource_tags(entity, complete_registry)  # type:ignore[arg-type]
        if results:
            for check, check_result in results.items():
                record = Record(check_id=check.id, check_name=check.name, check_result=check_result,
                                code_block=[],  # Don't show, could be large
                                file_path=self.extract_file_path_from_abs_path(Path(sls_file)),
                                file_line_range=entity_lines_range,
                                resource="complete",  # Weird, not sure what to put where
                                evaluations=variable_evaluations,
                                check_class=check.__class__.__module__,
                                file_abs_path=str(file_abs_path),
                                entity_tags=tags, severity=check.severity)
                record.set_guideline(check.guideline)
                report.add_record(record=record)
        else:
            report.extra_resources.add(
                ExtraResource(
                    file_abs_path=str(file_abs_path),
                    file_path=self.extract_file_path_from_abs_path(Path(sls_file)),
                    resource="complete",
                )
            )

    def single_item_sections_checks(self,
                                    sls_file: str,
                                    sls_file_data: dict[str, Any],
                                    report: Report,
                                    runner_filter: RunnerFilter,
                                    sls_context_parser: ContextParser) -> None:
        # Sub-sections that are a single item
        file_abs_path = Path(sls_file).absolute()
        for token, registry in SINGLE_ITEM_SECTIONS:
            item_content = sls_file_data.get(token)
            if not item_content:
                continue
            entity_lines_range, entity_code_lines = sls_context_parser.extract_code_lines(item_content)
            if not entity_lines_range:
                entity_code_lines = self.definitions_raw[sls_file]
                entity_lines_range = [1, len(entity_code_lines) - 1]

            skipped_checks = CfnContextParser.collect_skip_comments(entity_code_lines or [])
            variable_evaluations: dict[str, Any] = {}
            entity = EntityDetails(sls_context_parser.provider_type, item_content)
            results = registry.scan(sls_file, entity, skipped_checks, runner_filter)
            tags = get_resource_tags(entity, registry)
            fname = Path(sls_context_parser.file(item_content)).resolve()

            if results:
                for check, check_result in results.items():
                    censored_code_lines = omit_secret_value_from_checks(
                        check=check,
                        check_result=check_result,
                        entity_code_lines=entity_code_lines or [],
                        entity_config=item_content,
                        resource_attributes_to_omit=runner_filter.resource_attr_to_omit
                    )
                    record = Record(
                        check_id=check.id,
                        check_name=check.name,
                        check_result=check_result,
                        code_block=censored_code_lines,
                        file_path=self.extract_file_path_from_abs_path(fname),
                        file_line_range=entity_lines_range or [0, 0],
                        resource=token,
                        evaluations=variable_evaluations,
                        check_class=check.__class__.__module__,
                        file_abs_path=str(file_abs_path),
                        entity_tags=tags,
                        severity=check.severity,
                    )
                    record.set_guideline(check.guideline)
                    report.add_record(record=record)
            else:
                report.extra_resources.add(
                    ExtraResource(
                        file_abs_path=str(file_abs_path),
                        file_path=self.extract_file_path_from_abs_path(Path(sls_file)),
                        resource=token,
                    )
                )

    def multi_item_sections_checks(self,
                                   sls_file: str,
                                   sls_file_data: dict[str, Any],
                                   report: Report,
                                   runner_filter: RunnerFilter,
                                   sls_context_parser: ContextParser) -> None:
        # Sub-sections that have multiple items under them
        file_abs_path = Path(sls_file).absolute()
        for token, registry in MULTI_ITEM_SECTIONS:
            template_items = sls_file_data.get(token)
            if not template_items or not isinstance(template_items, dict):
                continue
            for item_name, item_content in template_items.items():
                if not isinstance(item_content, dict):
                    continue
                entity_lines_range, entity_code_lines = sls_context_parser.extract_code_lines(item_content)
                if entity_lines_range and entity_code_lines:
                    skipped_checks = CfnContextParser.collect_skip_comments(entity_code_lines)
                    variable_evaluations: dict[str, Any] = {}
                    if token == "functions":  # nosec
                        # "Enriching" copies things like "environment" and "stackTags" down into the
                        # function data from the provider block since logically that's what serverless
                        # does. This allows checks to see what the complete data would be.
                        sls_context_parser.enrich_function_with_provider(item_name)
                    entity = EntityDetails(sls_context_parser.provider_type, item_content)
                    results = registry.scan(sls_file, entity, skipped_checks, runner_filter)
                    tags = get_resource_tags(entity, registry)
                    fname = Path(sls_context_parser.file(item_content)).resolve()
                    if results:
                        for check, check_result in results.items():
                            censored_code_lines = omit_secret_value_from_checks(
                                check=check,
                                check_result=check_result,
                                entity_code_lines=entity_code_lines,
                                entity_config=item_content,
                                resource_attributes_to_omit=runner_filter.resource_attr_to_omit
                            )
                            record = Record(check_id=check.id, check_name=check.name, check_result=check_result,
                                            code_block=censored_code_lines,
                                            file_path=self.extract_file_path_from_abs_path(fname),
                                            file_line_range=entity_lines_range,
                                            resource=item_name, evaluations=variable_evaluations,
                                            check_class=check.__class__.__module__,
                                            file_abs_path=str(file_abs_path),
                                            entity_tags=tags, severity=check.severity)
                            record.set_guideline(check.guideline)
                            report.add_record(record=record)
                    else:
                        report.extra_resources.add(
                            ExtraResource(
                                file_abs_path=str(file_abs_path),
                                file_path=self.extract_file_path_from_abs_path(Path(sls_file)),
                                resource=item_name,
                            )
                        )

    def cfn_resources_checks(self,
                             sls_file: str,
                             sls_file_data: dict[str, Any],
                             report: Report,
                             runner_filter: RunnerFilter) -> None:
        file_abs_path = Path(sls_file).absolute()
        if CFN_RESOURCES_TOKEN in sls_file_data and isinstance(sls_file_data[CFN_RESOURCES_TOKEN], dict):
            cf_sub_template = sls_file_data[CFN_RESOURCES_TOKEN]
            cf_sub_resources = cf_sub_template.get("Resources")
            if cf_sub_resources and isinstance(cf_sub_resources, dict):
                cf_context_parser = CfnContextParser(sls_file, cf_sub_template, self.definitions_raw[sls_file])
                logging.debug(f"Template Dump for {sls_file}: {sls_file_data}")
                cf_context_parser.evaluate_default_refs()
                for resource_name, resource in cf_sub_resources.items():
                    if not isinstance(resource, dict):
                        continue
                    cf_resource_id = cf_context_parser.extract_cf_resource_id(resource, resource_name)
                    if not cf_resource_id:
                        # Not Type attribute for resource
                        continue
                    report.add_resource(f'{file_abs_path}:{cf_resource_id}')
                    entity_lines_range, entity_code_lines = cf_context_parser.extract_cf_resource_code_lines(
                        resource)
                    if entity_lines_range and entity_code_lines:
                        skipped_checks = CfnContextParser.collect_skip_comments(entity_code_lines)
                        # TODO - Variable Eval Message!
                        variable_evaluations: dict[str, Any] = {}

                        entity_dict = {resource_name: resource}
                        results = cfn_registry.scan(sls_file, entity_dict, skipped_checks, runner_filter)
                        tags = cfn_utils.get_resource_tags(entity_dict, cfn_registry)
                        if results:
                            for check, check_result in results.items():
                                censored_code_lines = omit_secret_value_from_checks(
                                    check=check,
                                    check_result=check_result,
                                    entity_code_lines=entity_code_lines,
                                    entity_config=resource,
                                    resource_attributes_to_omit=runner_filter.resource_attr_to_omit
                                )
                                record = Record(check_id=check.id, bc_check_id=check.bc_id, check_name=check.name,
                                                check_result=check_result,
                                                code_block=censored_code_lines,
                                                file_path=self.extract_file_path_from_abs_path(Path(sls_file)),
                                                file_line_range=entity_lines_range,
                                                resource=cf_resource_id, evaluations=variable_evaluations,
                                                check_class=check.__class__.__module__,
                                                file_abs_path=str(file_abs_path),
                                                entity_tags=tags, severity=check.severity)
                                record.set_guideline(check.guideline)
                                report.add_record(record=record)
                        else:
                            report.extra_resources.add(
                                ExtraResource(
                                    file_abs_path=str(file_abs_path),
                                    file_path=self.extract_file_path_from_abs_path(Path(sls_file)),
                                    resource=cf_resource_id,
                                )
                            )

    def extract_file_path_from_abs_path(self, path: Path) -> str:
        return f"{os.path.sep}{os.path.relpath(path, self.root_folder)}"

    def set_definitions_raw(self, definitions_raw: dict[str, list[tuple[int, str]]]) -> None:
        self.definitions_raw = definitions_raw
