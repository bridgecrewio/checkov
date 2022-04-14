import json
import logging
import os
from typing import Optional, List, Type

from checkov.cloudformation import cfn_utils
from checkov.cloudformation.cfn_utils import create_definitions, build_definitions_context
from checkov.cloudformation.checks.resource.registry import cfn_registry
from checkov.cloudformation.context_parser import ContextParser
from checkov.cloudformation.graph_builder.graph_components.block_types import BlockType
from checkov.cloudformation.parser.cfn_keywords import TemplateSections
from checkov.cloudformation.graph_builder.graph_to_definitions import convert_graph_vertices_to_definitions
from checkov.cloudformation.graph_builder.local_graph import CloudformationLocalGraph
from checkov.cloudformation.graph_manager import CloudformationGraphManager
from checkov.common.checks_infra.registry import get_graph_checks_registry
from checkov.common.graph.checks_infra.registry import BaseRegistry
from checkov.common.graph.db_connectors.networkx.networkx_db_connector import NetworkxConnector
from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.graph.graph_builder.local_graph import LocalGraph
from checkov.common.graph.graph_manager import GraphManager
from checkov.common.output.graph_record import GraphRecord
from checkov.common.output.record import Record
from checkov.common.output.report import Report, merge_reports, CheckType
from checkov.common.runners.base_runner import BaseRunner
from checkov.runner_filter import RunnerFilter


class Runner(BaseRunner):
    check_type = CheckType.CLOUDFORMATION

    def __init__(
        self,
        db_connector: NetworkxConnector = NetworkxConnector(),
        source: str = "CloudFormation",
        graph_class: Type[LocalGraph] = CloudformationLocalGraph,
        graph_manager: Optional[GraphManager] = None,
        external_registries: Optional[List[BaseRegistry]] = None,
    ) -> None:
        self.external_registries = [] if external_registries is None else external_registries
        self.graph_class = graph_class
        self.graph_manager = (
            graph_manager
            if graph_manager is not None
            else CloudformationGraphManager(source=source, db_connector=db_connector)
        )
        self.definitions_raw = {}
        self.graph_registry = get_graph_checks_registry(self.check_type)

    def run(
        self,
        root_folder: str,
        external_checks_dir: Optional[List[str]] = None,
        files: Optional[List[str]] = None,
        runner_filter: RunnerFilter = RunnerFilter(),
        collect_skip_comments: bool = True,
    ) -> Report:
        report = Report(self.check_type)
        parsing_errors = {}

        if self.context is None or self.definitions is None or self.breadcrumbs is None:
            self.definitions, self.definitions_raw = create_definitions(root_folder, files, runner_filter, parsing_errors)
            if external_checks_dir:
                for directory in external_checks_dir:
                    cfn_registry.load_external_checks(directory)
                    self.graph_registry.load_external_checks(directory)
            self.context = build_definitions_context(self.definitions, self.definitions_raw)

            logging.info("creating cloudformation graph")
            local_graph = self.graph_manager.build_graph_from_definitions(self.definitions)
            for vertex in local_graph.vertices:
                if vertex.block_type == BlockType.RESOURCE:
                    report.add_resource(f'{vertex.path}:{vertex.id}')
            self.graph_manager.save_graph(local_graph)
            self.definitions, self.breadcrumbs = convert_graph_vertices_to_definitions(local_graph.vertices, root_folder)

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

        report.add_parsing_errors(list(parsing_errors.keys()))
        # run checks
        self.check_definitions(root_folder, runner_filter, report)

        # run graph checks
        graph_report = self.get_graph_checks_report(root_folder, runner_filter)
        merge_reports(report, graph_report)

        return report

    def check_definitions(self, root_folder, runner_filter, report):
        for file_abs_path, definition in self.definitions.items():

            cf_file = f"/{os.path.relpath(file_abs_path, root_folder)}"

            if isinstance(definition, dict) and TemplateSections.RESOURCES in definition.keys():
                for resource_name, resource in definition[TemplateSections.RESOURCES].items():
                    resource_id = ContextParser.extract_cf_resource_id(resource, resource_name)
                    # check that the resource can be parsed as a CF resource
                    if resource_id:
                        resource_context = self.context[file_abs_path][
                            TemplateSections.RESOURCES][resource_name]
                        entity_lines_range = [resource_context['start_line'], resource_context['end_line']]
                        entity_code_lines = resource_context['code_lines']
                        if entity_lines_range and entity_code_lines:
                            # TODO - Variable Eval Message!
                            variable_evaluations = {}
                            skipped_checks = resource_context.get("skipped_checks")
                            entity = {resource_name: resource}
                            results = cfn_registry.scan(cf_file, entity, skipped_checks, runner_filter)
                            tags = cfn_utils.get_resource_tags(entity)
                            for check, check_result in results.items():
                                record = Record(
                                    check_id=check.id,
                                    bc_check_id=check.bc_id,
                                    check_name=check.name,
                                    check_result=check_result,
                                    code_block=entity_code_lines,
                                    file_path=cf_file,
                                    file_line_range=entity_lines_range,
                                    resource=resource_id,
                                    evaluations=variable_evaluations,
                                    check_class=check.__class__.__module__,
                                    file_abs_path=file_abs_path,
                                    entity_tags=tags,
                                    severity=check.severity
                                )

                                breadcrumb = self.breadcrumbs.get(record.file_path, {}).get(record.resource)
                                if breadcrumb:
                                    record = GraphRecord(record, breadcrumb)
                                record.set_guideline(check.guideline)
                                report.add_record(record=record)

    def get_graph_checks_report(self, root_folder: str, runner_filter: RunnerFilter) -> Report:
        report = Report(self.check_type)
        checks_results = self.run_graph_checks_results(runner_filter)

        for check, check_results in checks_results.items():
            for check_result in check_results:
                entity = check_result["entity"]
                if entity.get(CustomAttributes.BLOCK_TYPE) != BlockType.RESOURCE:
                    continue
                entity_file_abs_path = entity.get(CustomAttributes.FILE_PATH)
                entity_file_path = f"/{os.path.relpath(entity_file_abs_path, root_folder)}"
                entity_name = entity.get(CustomAttributes.BLOCK_NAME).split(".")[-1]
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
                    resource=entity.get(CustomAttributes.ID),
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
