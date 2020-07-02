import logging
import os

from checkov.arm.registry import arm_registry
from checkov.cloudformation.parser import parse
from checkov.common.output.record import Record
from checkov.common.output.report import Report
from checkov.common.runners.base_runner import BaseRunner, filter_ignored_directories
from checkov.runner_filter import RunnerFilter
from checkov.cloudformation.parser.node import dict_node
from checkov.arm.context_parser import ContextParser

ARM_POSSIBLE_ENDINGS = [".json"]


class Runner(BaseRunner):
    check_type = "arm"

    def run(self, root_folder, external_checks_dir=None, files=None, runner_filter=RunnerFilter()):
        report = Report(self.check_type)
        definitions = {}
        definitions_raw = {}
        parsing_errors = {}
        files_list = []
        if external_checks_dir:
            for directory in external_checks_dir:
                arm_registry.load_external_checks(directory)

        if files:
            for file in files:
                (definitions[file], definitions_raw[file]) = parse(file)

        if root_folder:
            for root, d_names, f_names in os.walk(root_folder):
                filter_ignored_directories(d_names)
                for file in f_names:
                    file_ending = os.path.splitext(file)[1]
                    if file_ending in ARM_POSSIBLE_ENDINGS:
                        files_list.append(os.path.join(root, file))

            for file in files_list:
                relative_file_path = f'/{os.path.relpath(file, os.path.commonprefix((root_folder, file)))}'
                (definitions[relative_file_path], definitions_raw[relative_file_path]) = parse(file)

        # Filter out empty files that have not been parsed successfully, and filter out non-CF template files
        definitions = {k: v for k, v in definitions.items() if v and v.__contains__("resources")}
        definitions_raw = {k: v for k, v in definitions_raw.items() if k in definitions.keys()}

        for arm_file in definitions.keys():
            if isinstance(definitions[arm_file], dict_node) and 'resources' in definitions[arm_file].keys():
                arm_context_parser = ContextParser(arm_file, definitions[arm_file], definitions_raw[arm_file])
                logging.debug("Template Dump for {}: {}".format(arm_file, definitions[arm_file], indent=2))
                arm_context_parser.evaluate_default_parameters()
                for resource in definitions[arm_file]['resources']:
                    resource_id = arm_context_parser.extract_arm_resource_id(resource)
                    resource_name = arm_context_parser.extract_arm_resource_name(resource)
                    entity_lines_range, entity_code_lines = arm_context_parser.extract_arm_resource_code_lines(resource)
                    if entity_lines_range and entity_code_lines:
                        # TODO - Variable Eval Message!
                        variable_evaluations = {}

                        skipped_checks = ContextParser.collect_skip_comments(resource)

                        results = arm_registry.scan(arm_file, {resource_name: resource}, skipped_checks,
                                                    runner_filter)
                        for check, check_result in results.items():
                            record = Record(check_id=check.id, check_name=check.name, check_result=check_result,
                                            code_block=entity_code_lines, file_path=arm_file,
                                            file_line_range=entity_lines_range,
                                            resource=resource_id, evaluations=variable_evaluations,
                                            check_class=check.__class__.__module__)
                            report.add_record(record=record)
        return report
