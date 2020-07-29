import logging
import os
from checkov.cloudformation.context_parser import ContextParser as CfnContextParser
from checkov.serverless.parsers.context_parser import ContextParser as SlsContextParser
from checkov.cloudformation.checks.resource.registry import cfn_registry
from checkov.serverless.registry import sls_registry
from checkov.common.runners.base_runner import BaseRunner, filter_ignored_directories
from checkov.runner_filter import RunnerFilter
from checkov.common.output.record import Record
from checkov.common.output.report import Report
from checkov.serverless.parsers.parser import parse
from checkov.cloudformation.parser.node import dict_node
from checkov.serverless.parsers.parser import FUNCTIONS_TOKEN, CFN_RESOURCES_TOKEN

SLS_FILE_MASK = ["serverless.yml", "serverless.yaml"]


class Runner(BaseRunner):
    check_type = "serverless"

    def run(self, root_folder, external_checks_dir=None, files=None, runner_filter=RunnerFilter()):
        report = Report(self.check_type)
        definitions = {}
        definitions_raw = {}
        parsing_errors = {}
        files_list = []
        if external_checks_dir:
            for directory in external_checks_dir:
                sls_registry.load_external_checks(directory, runner_filter)

        if files:
            for file in files:
                if file in SLS_FILE_MASK:
                    parse_result = parse(file)
                    if parse_result:
                        (definitions[file], definitions_raw[file]) = parse_result

        if root_folder:
            for root, d_names, f_names in os.walk(root_folder):
                filter_ignored_directories(d_names)
                for file in f_names:
                    if file in SLS_FILE_MASK:
                        full_path = os.path.join(root, file)
                        if 'node_modules' not in full_path and "/." not in full_path:
                            # skip temp directories
                            files_list.append(full_path)

            for file in files_list:
                relative_file_path = f'/{os.path.relpath(file, os.path.commonprefix((root_folder, file)))}'
                parse_result = parse(file)
                if parse_result:
                    (definitions[relative_file_path], definitions_raw[relative_file_path]) = parse_result

        # Filter out empty files that have not been parsed successfully
        definitions = {k: v for k, v in definitions.items() if v}
        definitions_raw = {k: v for k, v in definitions_raw.items() if k in definitions.keys()}

        for sls_file in definitions.keys():
            if isinstance(definitions[sls_file], dict_node):
                if CFN_RESOURCES_TOKEN in definitions[sls_file]:
                    cf_sub_template = definitions[sls_file][CFN_RESOURCES_TOKEN]
                    cf_context_parser = CfnContextParser(sls_file, cf_sub_template, definitions_raw[sls_file])
                    logging.debug("Template Dump for {}: {}".format(sls_file, definitions[sls_file], indent=2))
                    cf_context_parser.evaluate_default_refs()
                    for resource_name, resource in cf_sub_template['Resources'].items():
                        if not isinstance(resource, dict_node):
                            continue
                        cf_resource_id = cf_context_parser.extract_cf_resource_id(resource, resource_name)
                        entity_lines_range, entity_code_lines = cf_context_parser.extract_cf_resource_code_lines(
                            resource)
                        if entity_lines_range and entity_code_lines:
                            skipped_checks = CfnContextParser.collect_skip_comments(entity_code_lines)
                            # TODO - Variable Eval Message!
                            variable_evaluations = {}

                            results = cfn_registry.scan(sls_file, {resource_name: resource}, skipped_checks,
                                                        runner_filter)
                            for check, check_result in results.items():
                                record = Record(check_id=check.id, check_name=check.name, check_result=check_result,
                                                code_block=entity_code_lines, file_path=sls_file,
                                                file_line_range=entity_lines_range,
                                                resource=cf_resource_id, evaluations=variable_evaluations,
                                                check_class=check.__class__.__module__)
                                report.add_record(record=record)
                if FUNCTIONS_TOKEN in definitions[sls_file]:
                    template_functions = definitions[sls_file][FUNCTIONS_TOKEN]
                    sls_context_parser = SlsContextParser(sls_file, definitions[sls_file], definitions_raw[sls_file])
                    for sls_function_name, sls_function in template_functions.items():
                        if not isinstance(sls_function, dict_node):
                            continue
                        entity_lines_range, entity_code_lines = sls_context_parser.extract_function_code_lines(
                            sls_function)
                        if entity_lines_range and entity_code_lines:
                            skipped_checks = CfnContextParser.collect_skip_comments(entity_code_lines)
                            variable_evaluations = {}
                            sls_context_parser.enrich_function_with_provider(sls_function_name)
                            results = sls_registry.scan(sls_file, {'function': sls_function,
                                                                   'provider_type': sls_context_parser.provider_type},
                                                        skipped_checks, runner_filter)
                            for check, check_result in results.items():
                                record = Record(check_id=check.id, check_name=check.name, check_result=check_result,
                                                code_block=entity_code_lines, file_path=sls_file,
                                                file_line_range=entity_lines_range,
                                                resource=sls_function_name, evaluations=variable_evaluations,
                                                check_class=check.__class__.__module__)
                                report.add_record(record=record)

        return report
