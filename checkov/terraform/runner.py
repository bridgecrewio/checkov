import logging
import os

import dpath.util

from checkov.common.output.record import Record
from checkov.common.output.report import Report
from checkov.terraform.checks.data.registry import data_registry
from checkov.terraform.checks.provider.registry import provider_registry
from checkov.terraform.checks.resource.registry import resource_registry
from checkov.terraform.context_parsers.registry import parser_registry
from checkov.terraform.evaluation.base_variable_evaluation import BaseVariableEvaluation
from checkov.terraform.evaluation.evaluation_methods.const_variable_evaluation import ConstVariableEvaluation
from checkov.terraform.parser import Parser


class Runner:
    check_type = "terraform"

    def __init__(self, parser=Parser()):
        self.parser = parser

    block_type_registries = {
        'resource': resource_registry,
        'data': data_registry,
        'provider': provider_registry
    }

    def run(self, root_folder, external_checks_dir=None, files=None):
        report = Report(self.check_type)
        tf_definitions = {}
        parsing_errors = {}
        if external_checks_dir:
            for directory in external_checks_dir:
                resource_registry.load_external_checks(directory)
        if root_folder:
            root_folder = os.path.abspath(root_folder)
            self.parser.hcl2(directory=root_folder, tf_definitions=tf_definitions, parsing_errors=parsing_errors)
            self.check_tf_definition(report, root_folder, tf_definitions)

        if files:
            files = [os.path.abspath(file) for file in files]
            root_folder = os.path.split(os.path.commonprefix(files))[0]
            for file in files:
                file_tf_definitions = {}
                self.parser.parse_file(file=file, tf_definitions=file_tf_definitions, parsing_errors=parsing_errors)

                self.check_tf_definition(report, root_folder, file_tf_definitions)

        report.add_parsing_errors(parsing_errors.keys())

        return report

    def check_tf_definition(self, report, root_folder, tf_definitions):
        definitions_context = {}
        for definition in tf_definitions.items():
            definitions_context = parser_registry.enrich_definitions_context(definition)
        variable_evaluator = ConstVariableEvaluation(root_folder, tf_definitions, definitions_context)
        variable_evaluator.evaluate_variables()
        tf_definitions, definitions_context = variable_evaluator.tf_definitions, variable_evaluator.definitions_context
        for definition in tf_definitions.items():
            full_file_path = definition[0]
            scanned_file = definition[0].split(root_folder)[1]
            logging.debug(f"Scanning file: {scanned_file}")
            for block_type in definition[1].keys():
                if block_type in ['resource', 'data', 'provider']:
                    self.run_block(definition[1][block_type], definitions_context, full_file_path, report, scanned_file,
                                   block_type)

    def run_block(self, entities, definition_context, full_file_path, report, scanned_file, block_type):
        registry = self.block_type_registries[block_type]
        if registry:
            for entity in entities:
                entity_evaluations = None
                context_parser = parser_registry.context_parsers[block_type]
                definition_path = context_parser.get_entity_context_path(entity)
                entity_id = ".".join(definition_path)
                entity_context_path = [block_type] + definition_path
                if dpath.search(definition_context[full_file_path], entity_context_path):
                    entity_context = dpath.get(definition_context[full_file_path],
                                               entity_context_path)
                    entity_lines_range = [entity_context.get('start_line'), entity_context.get('end_line')]
                    entity_code_lines = entity_context.get('code_lines')
                    skipped_checks = entity_context.get('skipped_checks')
                    variables_evaluations = definition_context[full_file_path].get('evaluations')
                    if variables_evaluations:
                        entity_evaluations = BaseVariableEvaluation.reduce_entity_evaluations(variables_evaluations,
                                                                                               entity_context_path)
                    results = registry.scan(scanned_file, entity,
                                            skipped_checks)
                    for check, check_result in results.items():
                        record = Record(check_id=check.id, check_name=check.name, check_result=check_result,
                                        code_block=entity_code_lines, file_path=scanned_file,
                                        file_line_range=entity_lines_range,
                                        resource=entity_id, evaluations=entity_evaluations,
                                        check_class=check.__class__.__module__)
                        report.add_record(record=record)
