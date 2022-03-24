import json
import logging
import os
from typing import Optional, List

from checkov.common.checks_infra.registry import get_graph_checks_registry
from checkov.common.graph.graph_builder.graph_components.attribute_names import CustomAttributes

from checkov.common.output.record import Record
from checkov.common.output.report import Report, CheckType
from checkov.common.runners.base_runner import filter_ignored_paths
from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.registry import resource_registry
from checkov.terraform.context_parsers.registry import parser_registry
from checkov.terraform.plan_parser import parse_tf_plan
from checkov.terraform.runner import Runner as TerraformRunner, merge_reports


class Runner(TerraformRunner):
    check_type = CheckType.TERRAFORM_PLAN

    def __init__(self):
        super().__init__()
        self.template_lines = {}
        self.graph_registry = get_graph_checks_registry(super().check_type)

    block_type_registries = {
        'resource': resource_registry,
    }

    def run(
        self,
        root_folder: Optional[str] = None,
        external_checks_dir: Optional[List[str]] = None,
        files: Optional[List[str]] = None,
        runner_filter: RunnerFilter = RunnerFilter(),
        collect_skip_comments: bool = True
    ) -> Report:
        report = Report(self.check_type)
        self.tf_definitions = {}
        parsing_errors = {}
        if external_checks_dir:
            for directory in external_checks_dir:
                resource_registry.load_external_checks(directory)
                self.graph_registry.load_external_checks(directory)

        if root_folder:
            files = [] if not files else files
            for root, d_names, f_names in os.walk(root_folder):
                filter_ignored_paths(root, d_names, runner_filter.excluded_paths)
                filter_ignored_paths(root, f_names, runner_filter.excluded_paths)
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
                            parsing_errors[file] = str(e)

        if files:
            files = [os.path.abspath(file) for file in files]
            for file in files:
                if file.endswith(".json"):
                    tf_definitions, template_lines = parse_tf_plan(file, parsing_errors)
                    if not tf_definitions:
                        continue
                    self.tf_definitions = tf_definitions
                    self.template_lines = template_lines
                    self.check_tf_definition(report, runner_filter)
                else:
                    logging.debug(f'Failed to load {file} as is not a .json file, skipping')

        report.add_parsing_errors(parsing_errors.keys())

        if self.tf_definitions:
            graph = self.graph_manager.build_graph_from_definitions(self.tf_definitions, render_variables=False)
            self.graph_manager.save_graph(graph)

            graph_report = self.get_graph_checks_report(root_folder, runner_filter)
            merge_reports(report, graph_report)

        return report

    def get_entity_context_and_evaluations(self, entity):
        raw_context = self.get_entity_context(entity[CustomAttributes.BLOCK_NAME].split("."), entity[CustomAttributes.FILE_PATH])
        raw_context['definition_path'] = entity[CustomAttributes.BLOCK_NAME].split('.')
        return raw_context, None

    def check_tf_definition(self, report, runner_filter):
        for full_file_path, definition in self.tf_definitions.items():
            scanned_file = f"/{os.path.relpath(full_file_path)}"
            logging.debug(f"Scanning file: {scanned_file}")
            for block_type in definition.keys():
                if block_type in self.block_type_registries.keys():
                    self.run_block(definition[block_type], full_file_path, report, scanned_file,
                                   block_type, runner_filter)

    def run_block(self, entities, full_file_path, report, scanned_file, block_type, runner_filter=None):
        registry = self.block_type_registries[block_type]
        if registry:
            for entity in entities:
                context_parser = parser_registry.context_parsers[block_type]
                definition_path = context_parser.get_entity_context_path(entity)
                entity_id = ".".join(definition_path)
                # Entity can exist only once per dir, for file as well
                entity_context = self.get_entity_context(definition_path, full_file_path)
                entity_lines_range = [entity_context.get('start_line'), entity_context.get('end_line')]
                entity_code_lines = entity_context.get('code_lines')
                entity_address = entity_context.get('address')

                results = registry.scan(scanned_file, entity, [], runner_filter)
                for check, check_result in results.items():
                    record = Record(check_id=check.id, bc_check_id=check.bc_id, check_name=check.name, check_result=check_result,
                                    code_block=entity_code_lines, file_path=scanned_file,
                                    file_line_range=entity_lines_range,
                                    resource=entity_id, resource_address=entity_address, evaluations=None,
                                    check_class=check.__class__.__module__, file_abs_path=full_file_path,
                                    severity=check.severity)
                    record.set_guideline(check.guideline)
                    report.add_record(record=record)

    def get_entity_context(self, definition_path, full_file_path):
        entity_context = {}

        if full_file_path not in self.tf_definitions:
            logging.debug(f'Tried to look up file {full_file_path} in TF plan entity definitions, but it does not exist')
            return entity_context

        for resource in self.tf_definitions.get(full_file_path, {}).get('resource', []):
            resource_type = definition_path[0]
            if resource_type in resource.keys():
                resource_name = definition_path[1]
                if resource_name in resource[resource_type].keys():
                    resource_defintion = resource[resource_type][resource_name]
                    entity_context['start_line'] = resource_defintion['start_line'][0]
                    entity_context['end_line'] = resource_defintion['end_line'][0]
                    entity_context['code_lines'] = self.template_lines[
                                                   entity_context['start_line']:entity_context['end_line']]
                    entity_context['address'] = resource_defintion['__address__']
                    return entity_context
        return entity_context
