from __future__ import annotations

import json
import logging
import os
from typing import Type, Any, TYPE_CHECKING

from checkov.cloudformation import cfn_utils
from checkov.cloudformation.cfn_utils import create_definitions, build_definitions_context
from checkov.cloudformation.checks.resource.registry import cfn_registry
from checkov.cloudformation.context_parser import ContextParser
from checkov.cloudformation.graph_builder.graph_components.block_types import BlockType
from checkov.cloudformation.graph_builder.graph_to_definitions import convert_graph_vertices_to_definitions
from checkov.cloudformation.graph_builder.local_graph import CloudformationLocalGraph
from checkov.cloudformation.graph_manager import CloudformationGraphManager
from checkov.cloudformation.image_referencer.manager import CloudFormationImageReferencerManager
from checkov.cloudformation.parser.cfn_keywords import TemplateSections
from checkov.common.checks_infra.registry import get_graph_checks_registry
from checkov.common.graph.checks_infra.registry import BaseRegistry
from checkov.common.typing import LibraryGraphConnector
from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.graph.graph_builder.consts import GraphSource
from checkov.common.images.image_referencer import ImageReferencerMixin
from checkov.common.output.extra_resource import ExtraResource
from checkov.common.output.graph_record import GraphRecord
from checkov.common.output.record import Record
from checkov.common.output.report import Report, merge_reports, CheckType
from checkov.common.runners.base_runner import BaseRunner, CHECKOV_CREATE_GRAPH
from checkov.common.util.secrets import omit_secret_value_from_checks
from checkov.runner_filter import RunnerFilter

if TYPE_CHECKING:
    from networkx import DiGraph
    from checkov.common.checks_infra.registry import Registry
    from checkov.common.images.image_referencer import Image


class Runner(ImageReferencerMixin[None], BaseRunner[CloudformationGraphManager]):
    check_type = CheckType.CLOUDFORMATION  # noqa: CCE003  # a static attribute

    def __init__(
            self,
            db_connector: LibraryGraphConnector | None = None,
            source: str = GraphSource.CLOUDFORMATION,
            graph_class: Type[CloudformationLocalGraph] = CloudformationLocalGraph,
            graph_manager: CloudformationGraphManager | None = None,
            external_registries: list[BaseRegistry] | None = None
    ) -> None:
        super().__init__(file_extensions=['.json', '.yml', '.yaml', '.template'])
        db_connector = db_connector or self.db_connector
        self.external_registries = [] if external_registries is None else external_registries
        self.graph_class = graph_class
        self.graph_manager: CloudformationGraphManager = (
            graph_manager
            if graph_manager is not None
            else CloudformationGraphManager(source=source, db_connector=db_connector)
        )
        self.context: "dict[str, dict[str, Any]]" = {}
        self.definitions: "dict[str, dict[str, Any]]" = {}  # type:ignore[assignment]  # need to check, how to support subclass differences
        self.definitions_raw: "dict[str, list[tuple[int, str]]]" = {}
        self.graph_registry: "Registry" = get_graph_checks_registry(self.check_type)

    def run(
            self,
            root_folder: str | None,
            external_checks_dir: list[str] | None = None,
            files: list[str] | None = None,
            runner_filter: RunnerFilter | None = None,
            collect_skip_comments: bool = True,
    ) -> Report | list[Report]:
        runner_filter = runner_filter or RunnerFilter()
        if not runner_filter.show_progress_bar:
            self.pbar.turn_off_progress_bar()

        report = Report(self.check_type)
        parsing_errors: dict[str, str] = {}

        if self.context is None or self.definitions is None or self.breadcrumbs is None:
            self.definitions, self.definitions_raw = create_definitions(root_folder, files, runner_filter,
                                                                        parsing_errors)
            report.add_parsing_errors(list(parsing_errors.keys()))

            if external_checks_dir:
                for directory in external_checks_dir:
                    cfn_registry.load_external_checks(directory)

                    if CHECKOV_CREATE_GRAPH:
                        self.graph_registry.load_external_checks(directory)

            self.context = build_definitions_context(self.definitions, self.definitions_raw)

            if CHECKOV_CREATE_GRAPH:
                logging.info("creating CloudFormation graph")
                local_graph = self.graph_manager.build_graph_from_definitions(self.definitions)
                logging.info("Successfully created CloudFormation graph")

                for vertex in local_graph.vertices:
                    if vertex.block_type == BlockType.RESOURCE:
                        report.add_resource(f'{vertex.path}:{vertex.id}')
                self.graph_manager.save_graph(local_graph)
                self.definitions, self.breadcrumbs = convert_graph_vertices_to_definitions(
                    vertices=local_graph.vertices,
                    root_folder=root_folder,
                )

        # TODO: replace with real graph rendering
        for cf_file in self.definitions.keys():
            file_definition = self.definitions.get(cf_file, None)
            file_definition_raw = self.definitions_raw.get(cf_file, None)
            if file_definition is not None and file_definition_raw is not None:
                cf_context_parser = ContextParser(cf_file, file_definition, file_definition_raw)
                logging.debug(
                    "Template Dump for {}: {}".format(cf_file, json.dumps(file_definition, indent=2, default=str))
                )
                cf_context_parser.evaluate_default_refs()

        self.pbar.initiate(len(self.definitions))

        # run checks
        self.check_definitions(root_folder, runner_filter, report)

        # run graph checks
        if CHECKOV_CREATE_GRAPH:
            graph_report = self.get_graph_checks_report(root_folder, runner_filter)
            merge_reports(report, graph_report)

        if runner_filter.run_image_referencer:
            if files:
                # 'root_folder' shouldn't be empty to remove the whole path later and only leave the shortened form
                root_folder = os.path.split(os.path.commonprefix(files))[0]

            image_report = self.check_container_image_references(
                graph_connector=self.graph_manager.get_reader_endpoint(),
                root_path=root_folder,
                runner_filter=runner_filter,
            )

            if image_report:
                # due too many tests failing only return a list, if there is an image report
                return [report, image_report]

        return report

    def check_definitions(self, root_folder: str | None, runner_filter: RunnerFilter, report: Report) -> None:
        for file_abs_path, definition in self.definitions.items():
            cf_file = f"/{os.path.relpath(file_abs_path, root_folder)}"
            self.pbar.set_additional_data({'Current File Scanned': cf_file})
            if isinstance(definition, dict) and TemplateSections.RESOURCES in definition.keys():
                for resource_name, resource in definition[TemplateSections.RESOURCES].items():
                    resource_id = ContextParser.extract_cf_resource_id(resource, resource_name)
                    # check that the resource can be parsed as a CF resource
                    if resource_id:
                        resource_context = self.context[file_abs_path][TemplateSections.RESOURCES][resource_name]
                        entity_lines_range = [resource_context['start_line'], resource_context['end_line']]
                        entity_code_lines = resource_context['code_lines']
                        if entity_lines_range and entity_code_lines:
                            # TODO - Variable Eval Message!
                            variable_evaluations: "dict[str, Any]" = {}
                            skipped_checks = resource_context.get("skipped_checks")
                            entity = {resource_name: resource}
                            results = cfn_registry.scan(cf_file, entity, skipped_checks, runner_filter)
                            tags = cfn_utils.get_resource_tags(entity)
                            if results:
                                for check, check_result in results.items():
                                    censored_code_lines = omit_secret_value_from_checks(
                                        check=check,
                                        check_result=check_result,
                                        entity_code_lines=entity_code_lines,
                                        entity_config=resource,
                                        resource_attributes_to_omit=runner_filter.resource_attr_to_omit
                                    )
                                    record = Record(
                                        check_id=check.id,
                                        bc_check_id=check.bc_id,
                                        check_name=check.name,
                                        check_result=check_result,
                                        code_block=censored_code_lines,
                                        file_path=cf_file,
                                        file_line_range=entity_lines_range,
                                        resource=resource_id,
                                        evaluations=variable_evaluations,
                                        check_class=check.__class__.__module__,
                                        file_abs_path=file_abs_path,
                                        entity_tags=tags,
                                        severity=check.severity
                                    )

                                    if CHECKOV_CREATE_GRAPH and self.breadcrumbs:
                                        breadcrumb = self.breadcrumbs.get(record.file_path, {}).get(record.resource)
                                        if breadcrumb:
                                            record = GraphRecord(record, breadcrumb)
                                    record.set_guideline(check.guideline)
                                    report.add_record(record=record)
                            else:
                                # resources without checks, but not existing ones
                                report.extra_resources.add(
                                    ExtraResource(
                                        file_abs_path=str(file_abs_path),
                                        file_path=cf_file,
                                        resource=resource_id,
                                    )
                                )
            self.pbar.update()
        self.pbar.close()

    def get_graph_checks_report(self, root_folder: str | None, runner_filter: RunnerFilter) -> Report:
        report = Report(self.check_type)
        checks_results = self.run_graph_checks_results(runner_filter, self.check_type)

        for check, check_results in checks_results.items():
            for check_result in check_results:
                entity = check_result["entity"]
                if entity.get(CustomAttributes.BLOCK_TYPE) != BlockType.RESOURCE:
                    continue
                entity_file_abs_path = entity[CustomAttributes.FILE_PATH]
                entity_file_path = f"/{os.path.relpath(entity_file_abs_path, root_folder)}"
                entity_name = entity[CustomAttributes.BLOCK_NAME].split(".")[-1]
                entity_context = self.context[entity_file_abs_path][TemplateSections.RESOURCES][
                    entity_name
                ]

                record = Record(
                    check_id=check.id,
                    check_name=check.name,
                    check_result=check_result,
                    code_block=entity_context.get("code_lines"),
                    file_path=entity_file_path,
                    file_line_range=[entity_context.get("start_line"), entity_context.get("end_line")],
                    resource=entity[CustomAttributes.ID],
                    evaluations={},
                    check_class=check.__class__.__module__,
                    file_abs_path=entity_file_abs_path,
                    entity_tags={} if not entity.get("Tags") else cfn_utils.parse_entity_tags(entity.get("Tags")),
                    severity=check.severity
                )
                if self.breadcrumbs:
                    breadcrumb = self.breadcrumbs.get(record.file_path, {}).get(record.resource)
                    if breadcrumb:
                        record = GraphRecord(record, breadcrumb)
                record.set_guideline(check.guideline)
                report.add_record(record=record)
        return report

    def extract_images(
        self,
        graph_connector: DiGraph | None = None,
        definitions: dict[str, dict[str, Any] | list[dict[str, Any]]] | None = None,
        definitions_raw: dict[str, list[tuple[int, str]]] | None = None
    ) -> list[Image]:
        if not graph_connector:
            # should not happen
            return []

        manager = CloudFormationImageReferencerManager(graph_connector=graph_connector)
        images: list[Image] = manager.extract_images_from_resources()

        return images
