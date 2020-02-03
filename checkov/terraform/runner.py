import logging
import os

from checkov.terraform.checks.data.registry import data_registry
from checkov.terraform.context_parsers.registry import parser_registry
from checkov.terraform.checks.resource.registry import resource_registry
from checkov.terraform.evaluation.evaluation_methods.const_variable_evaluation import ConstVariableEvaluation
from checkov.terraform.output.record import Record
from checkov.terraform.output.report import Report
from checkov.terraform.parser import Parser
import dpath.util


class Runner:
    def __init__(self, parser=Parser()):
        self.parser = parser

    block_type_registries = {
        'resource': resource_registry,
        'data': data_registry
    }

    def run(self, root_folder, external_checks_dir=None, files=None):
        report = Report()
        tf_definitions = {}
        parsing_errors = {}
        if external_checks_dir:
            for directory in external_checks_dir:
                resource_registry.load_external_checks(directory)
        if root_folder:
            self.parser.hcl2(directory=root_folder, tf_definitions=tf_definitions, parsing_errors=parsing_errors)
            self.check_tf_definition(report, root_folder, tf_definitions)

        if files:
            root_folder = os.path.commonprefix(files)
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
            logging.debug("Scanning file: %s", scanned_file)
            for block_type in definition[1].keys():
                if block_type in ['resource', 'data']:
                    self.run_block(definition[1][block_type], definitions_context, full_file_path, report, scanned_file,
                                   block_type)

    def run_block(self, entities, definition_context, full_file_path, report, scanned_file, block_type):
        for entity in entities:
            entity_type = list(entity.keys())[0]
            entity_name = list(list(entity.values())[0].keys())[0]
            entity_id = "{}.{}".format(entity_type, entity_name)
            if dpath.search(definition_context[full_file_path], f'**/{entity_type}/{entity_name}'):
                entity_context = dpath.get(definition_context[full_file_path], f'*/{entity_type}/{entity_name}')
                entity_lines_range = [entity_context.get('start_line'), entity_context.get('end_line')]
                entity_code_lines = entity_context.get('code_lines')
                skipped_checks = entity_context.get('skipped_checks')
                variable_evaluations = definition_context[full_file_path].get('evaluations')
                registry = self.block_type_registries[block_type]

                if registry:
                    results = registry.scan(entity, scanned_file, skipped_checks)
                    for check, check_result in results.items():
                        record = Record(check_id=check.id, check_name=check.name, check_result=check_result,
                                        code_block=entity_code_lines, file_path=scanned_file,
                                        file_line_range=entity_lines_range,
                                        resource=entity_id, evaluations=variable_evaluations,
                                        check_class=check.__class__.__module__)
                        report.add_record(record=record)
