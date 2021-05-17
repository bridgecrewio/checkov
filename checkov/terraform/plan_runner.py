from collections import defaultdict
import logging
import json
import logging
import os

from checkov.common.models.enums import CheckResult
from checkov.common.util import dict_utils
from checkov.common.output.record import Record
from checkov.common.output.report import Report
from checkov.common.runners.base_runner import BaseRunner
from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.registry import resource_registry
from checkov.terraform.runner import Runner as tf_runner
from checkov.terraform.parser import Parser
from checkov.terraform.context_parsers.registry import parser_registry
# Allow the evaluation of empty variables
from checkov.terraform.plan_parser import parse_tf_plan

CHECK_BLOCK_TYPES = frozenset(["resource", "data", "provider", "module"])

class Runner(BaseRunner):
    check_type = "terraform_plan"

    def __init__(self):
        self.tf_definitions = {}
        self.definitions_context = {}
        self.template_lines = {}

    block_type_registries = {
        'resource': resource_registry,
    }

    def run(self, root_folder=None, external_checks_dir=None, files=None, runner_filter=RunnerFilter(),
            collect_skip_comments=True):
        report = Report(self.check_type)
        self.tf_definitions = {}
        parsing_errors = {}
        if external_checks_dir:
            for directory in external_checks_dir:
                resource_registry.load_external_checks(directory)

        if root_folder:
            files = [] if not files else files
            for root, d_names, f_names in os.walk(root_folder):
                for file in f_names:
                    file_ending = os.path.splitext(file)[1]
                    if file_ending == '.json':
                        try:
                            with open(f'{root}/{file}') as f:
                                content = json.load(f)
                            if isinstance(content, dict) and content.get('terraform_version'):
                                files.append(os.path.join(root, file))
                        except Exception as e:
                            logging.debug(f'Failed to load json file {root}/{file}, skipping')
                            logging.debug('Failure message:')
                            logging.debug(e, stack_info=True)

        if files:
            files = [os.path.abspath(file) for file in files]
            for file in files:
                if file.endswith(".json"):
                    tf_definitions, template_lines = parse_tf_plan(file)
                    if not tf_definitions:
                        continue
                    self.tf_definitions = tf_definitions
                    self.template_lines = template_lines
                    self.check_tf_definition(report, runner_filter)
                else:
                    logging.debug(f'Failed to load {file} as is not a .json file, skipping')

        report.add_parsing_errors(parsing_errors.keys())

        enriched_resources = self.get_enriched_resources(report, '/Users/acotenoff/Development/tf-acotenoff-test/')
        reports = self.enrich_plan_records(report, enriched_resources)
        #reports = self.handle_skipped_checks(reports_without_skipped, enriched_resources)

        return reports

    def check_tf_definition(self, report, runner_filter,
                            ):

        for full_file_path, definition in self.tf_definitions.items():
            scanned_file = f"/{os.path.relpath(full_file_path)}"
            logging.debug(f"Scanning file: {scanned_file}")
            for block_type in definition.keys():
                if block_type in self.block_type_registries.keys():
                    self.run_block(definition[block_type], full_file_path, report, scanned_file,
                                   block_type, runner_filter)

    def run_block(self, entities, full_file_path, report, scanned_file, block_type,
                  runner_filter=None):
        registry = self.block_type_registries[block_type]
        if registry:
            for entity in entities:
                entity_evaluations = None
                context_parser = parser_registry.context_parsers[block_type]
                definition_path = context_parser.get_entity_context_path(entity)
                entity_id = ".".join(definition_path)
                # Entity can exist only once per dir, for file as well
                entity_context = self.get_entity_context(definition_path, full_file_path)
                entity_lines_range = [entity_context.get('start_line'), entity_context.get('end_line')]
                entity_code_lines = entity_context.get('code_lines')
                results = registry.scan(scanned_file, entity, [], runner_filter)
                for check, check_result in results.items():
                    record = Record(check_id=check.id, check_name=check.name, check_result=check_result,
                                    code_block=entity_code_lines, file_path=scanned_file,
                                    file_line_range=entity_lines_range,
                                    resource=entity_id, evaluations=entity_evaluations,
                                    check_class=check.__class__.__module__, file_abs_path=full_file_path)
                    report.add_record(record=record)

    def get_entity_context(self, definition_path, full_file_path):
        entity_context = {}
        for resource in self.tf_definitions[full_file_path]['resource']:
            resource_type = definition_path[0]
            if resource_type in resource.keys():
                resource_name = definition_path[1]
                if resource_name in resource[resource_type].keys():
                    resource_defintion = resource[resource_type][resource_name]
                    entity_context['start_line'] = resource_defintion['start_line'][0]
                    entity_context['end_line'] = resource_defintion['end_line'][0]
                    entity_context['code_lines'] = self.template_lines[entity_context['start_line']:entity_context['end_line']]
                    return entity_context
        return entity_context

    def get_enriched_resources(self, reports, repo_root):
        parser = Parser()
        tf_definitions = {}
        parsing_errors = {}
        Parser.parse_directory(
            parser,
            directory=repo_root,  # assume plan file is in the repo-root
            out_definitions=tf_definitions,
            out_parsing_errors=parsing_errors,
        )

        enriched_resources = defaultdict(dict)
        for definition in tf_definitions.items():
            definitions_context = parser_registry.enrich_definitions_context(definition)

        for full_file_path, definition in tf_definitions.items():
            abs_scanned_file, _ = tf_runner._strip_module_referrer(full_file_path)
            scanned_file = os.path.relpath(abs_scanned_file, repo_root)
            for block_type in definition.keys():
                if block_type in CHECK_BLOCK_TYPES:
                    for entity in definition[block_type]:
                        context_parser = parser_registry.context_parsers[block_type]
                        definition_path = context_parser.get_entity_context_path(entity)
                        entity_id = ".".join(definition_path)
                        entity_context_path = [block_type] + definition_path
                        entity_context = dict_utils.getInnerDict(
                            definitions_context[full_file_path], entity_context_path
                        )
                        entity_lines_range = [
                            entity_context.get("start_line"),
                            entity_context.get("end_line"),
                        ]
                        entity_code_lines = entity_context.get("code_lines")
                        enriched_resources[entity_id] = {
                            "entity_code_lines": entity_code_lines,
                            "entity_lines_range": entity_lines_range,
                            "scanned_file": scanned_file,
                        }

        return enriched_resources


    def enrich_plan_records(self, report, enriched_resources):
        # This enriches reports with the appropriate filepath, line numbers, and codeblock
        for record in report.failed_checks:
            if record.resource in enriched_resources:
                record.file_path = enriched_resources[record.resource]["scanned_file"]
                record.file_line_range = enriched_resources[record.resource][
                    "entity_lines_range"
                ]
                record.code_block = enriched_resources[record.resource][
                    "entity_code_lines"
                ]
        return report
