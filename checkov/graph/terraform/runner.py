import copy
import logging
import os
from typing import Dict

import dpath.util

from checkov.common.output.record import Record
from checkov.common.output.report import Report
from checkov.common.runners.base_runner import BaseRunner
from checkov.common.variables.context import EvaluationContext
from checkov.graph.terraform.checks.checks_infra.nx_checks_parser import NXGraphCheckParser
from checkov.graph.terraform.checks.checks_infra.registry import Registry
from checkov.graph.terraform.graph_builder.graph_components.attribute_names import CustomAttributes
from checkov.graph.parser import TerraformGraphParser
from checkov.graph.terraform.graph_manager import GraphManager
from checkov.graph.graph_record import GraphRecord
from checkov.graph.terraform.graph_builder.graph_to_tf_definitions import convert_graph_vertices_to_tf_definitions
from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.registry import resource_registry
from checkov.terraform.runner import Runner as TerraformRunner

LOG_LEVEL = os.getenv('LOG_LEVEL', 'WARNING').upper()
logging.basicConfig(level=LOG_LEVEL)


class TerraformGraphRunner(BaseRunner):
    check_type = "graph"

    def __init__(self, parser=TerraformGraphParser()):
        self.parser = parser
        self.tf_definitions = {}
        self.definitions_context = {}
        self.evaluations_context: Dict[str, Dict[str, EvaluationContext]] = {}
        self.graph_manager = GraphManager(source="Terraform")
        self.tf_runner = TerraformRunner()
        self.graph = None

    def run(self, root_folder, external_checks_dir=None, files=None, runner_filter=RunnerFilter(), collect_skip_comments=True):
        report = Report(self.check_type)
        self.tf_definitions = {}
        parsing_errors = {}
        breadcrumbs = {}
        if external_checks_dir:
            for directory in external_checks_dir:
                resource_registry.load_external_checks(directory, runner_filter)
        if root_folder:
            root_folder = os.path.abspath(root_folder)

            local_graph = self.graph_manager.build_graph_from_source_directory(root_folder)
            self.graph = self.graph_manager.save_graph(local_graph)
            self.tf_runner.tf_definitions, breadcrumbs = convert_graph_vertices_to_tf_definitions(local_graph.vertices, root_folder)
            self.tf_runner.check_tf_definition(report, root_folder, runner_filter, collect_skip_comments)

        if files:
            # TODO: support parsing a specific file!!
            files = [os.path.abspath(file) for file in files]
            root_folder = os.path.split(os.path.commonprefix(files))[0]
            for file in files:
                if file.endswith(".tf"):
                    file_parsing_errors = {}
                    parse_result = self.parser.parse_file(file=file, parsing_errors=file_parsing_errors)
                    if parse_result is not None:
                        self.tf_runner.tf_definitions[file] = parse_result
                    if file_parsing_errors:
                        parsing_errors.update(file_parsing_errors)
                        continue
                    self.tf_runner.check_tf_definition(report, root_folder, runner_filter, collect_skip_comments)

        report.add_parsing_errors(parsing_errors.keys())

        graph_report = self.get_graph_checks_report(root_folder, breadcrumbs)
        merge_reports(report, graph_report)

        return report

    def get_graph_checks_report(self, root_folder, breadcrumbs):
        registry = Registry(parser=NXGraphCheckParser())
        registry.load_checks()
        report = Report(self.check_type)
        checks_results = registry.run_checks(self.graph)
        for check_id, check_results in checks_results.items():
            for check_result in check_results:
                entity = check_result['entity']
                entity_context, entity_evaluations = self.get_entity_context_and_evaluations(entity)
                if entity_context:
                    full_file_path = entity[CustomAttributes.FILE_PATH]
                    copy_of_check_result = copy.deepcopy(check_result)
                    copy_of_check_result['entity'] = entity.get(CustomAttributes.CONFIG)
                    record = Record(check_id=check_id,
                                    check_name=check_id,
                                    check_result=copy_of_check_result,
                                    code_block=entity_context.get('code_lines'),
                                    file_path=f"/{os.path.relpath(full_file_path, root_folder)}",
                                    file_line_range=[entity_context.get('start_line'), entity_context.get('end_line')],
                                    resource=".".join(entity_context['definition_path']),
                                    evaluations=entity_evaluations,
                                    check_class=check_id,
                                    file_abs_path=os.path.abspath(full_file_path))
                    breadcrumb = breadcrumbs.get(record.file_path, {}).get(record.resource)
                    if breadcrumb:
                        record = GraphRecord(record, breadcrumb)

                    report.add_record(record=record)
        return report
        
    def get_entity_context_and_evaluations(self, entity):
        entity_evaluations = None
        block_type = entity[CustomAttributes.BLOCK_TYPE]
        full_file_path = entity[CustomAttributes.FILE_PATH]
        definition_path = entity[CustomAttributes.BLOCK_NAME].split('.')
        entity_context = None
        entity_context_path = [block_type] + definition_path
        if dpath.search(self.tf_runner.definitions_context.get(full_file_path), entity_context_path):
            entity_context = dpath.get(self.tf_runner.definitions_context[full_file_path],
                                       entity_context_path)
            entity_context['definition_path'] = definition_path
        return entity_context, entity_evaluations


def merge_reports(base_report, report_to_merge):
    base_report.passed_checks.extend(report_to_merge.passed_checks)
    base_report.failed_checks.extend(report_to_merge.failed_checks)
    base_report.skipped_checks.extend(report_to_merge.skipped_checks)
    base_report.parsing_errors.extend(report_to_merge.parsing_errors)