import logging
import os

from checkov.cloudformation import cfn_utils
from checkov.cloudformation.context_parser import ContextParser as CfnContextParser
from checkov.serverless.base_registry import EntityDetails
from checkov.serverless.parsers.context_parser import ContextParser as SlsContextParser
from checkov.cloudformation.checks.resource.registry import cfn_registry
from checkov.serverless.checks.complete.registry import complete_registry
from checkov.serverless.checks.custom.registry import custom_registry
from checkov.serverless.checks.function.registry import function_registry
from checkov.serverless.checks.layer.registry import layer_registry
from checkov.serverless.checks.package.registry import package_registry
from checkov.serverless.checks.plugin.registry import plugin_registry
from checkov.serverless.checks.provider.registry import provider_registry
from checkov.serverless.checks.service.registry import service_registry
from checkov.common.runners.base_runner import BaseRunner, filter_ignored_directories
from checkov.runner_filter import RunnerFilter
from checkov.common.output.record import Record
from checkov.common.output.report import Report
from checkov.serverless.parsers.parser import parse
from checkov.cloudformation.parser.node import dict_node
from checkov.serverless.parsers.parser import CFN_RESOURCES_TOKEN

SLS_FILE_MASK = ["serverless.yml", "serverless.yaml"]

MULTI_ITEM_SECTIONS = [
    ("functions", function_registry),
    ("layers", layer_registry)
]
SINGLE_ITEM_SECTIONS = [
    ("custom", custom_registry),
    ("package", package_registry),
    ("plugins", plugin_registry),
    ("provider", provider_registry),
    ("service", service_registry)
]


class Runner(BaseRunner):
    check_type = "serverless"

    def run(self, root_folder, external_checks_dir=None, files=None, runner_filter=RunnerFilter(), collect_skip_comments=True):
        report = Report(self.check_type)
        definitions = {}
        definitions_raw = {}
        parsing_errors = {}
        files_list = []
        if external_checks_dir:
            for directory in external_checks_dir:
                function_registry.load_external_checks(directory, runner_filter)

        if files:
            for file in files:
                if os.path.basename(file) in SLS_FILE_MASK:
                    parse_result = parse(file)
                    if parse_result:
                        (definitions[file], definitions_raw[file]) = parse_result

        if root_folder:
            for root, d_names, f_names in os.walk(root_folder):
                # Don't walk in to "node_modules" directories under the root folder. If –for some reason–
                # scanning one of these is desired, it can be directly specified.
                if "node_modules" in d_names:
                    d_names.remove("node_modules")

                filter_ignored_directories(d_names)
                for file in f_names:
                    if file in SLS_FILE_MASK:
                        full_path = os.path.join(root, file)
                        if "/." not in full_path:
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

        for sls_file, sls_file_data in definitions.items():

            # There are a few cases here. If -f was used, there could be a leading / because it's an absolute path,
            # or there will be no leading slash; root_folder will always be none.
            # If -d is used, root_folder will be the value given, and -f will start with a / (hardcoded above).
            # The goal here is simply to get a valid path to the file (which sls_file does not always give).
            if sls_file[0] == '/':
                path_to_convert = (root_folder + sls_file) if root_folder else sls_file
            else:
                path_to_convert = (os.path.join(root_folder, sls_file)) if root_folder else sls_file

            file_abs_path = os.path.abspath(path_to_convert)

            if not isinstance(sls_file_data, dict_node):
                continue

            if CFN_RESOURCES_TOKEN in sls_file_data and isinstance(sls_file_data[CFN_RESOURCES_TOKEN], dict_node):
                cf_sub_template = sls_file_data[CFN_RESOURCES_TOKEN]
                cf_context_parser = CfnContextParser(sls_file, cf_sub_template, definitions_raw[sls_file])
                logging.debug("Template Dump for {}: {}".format(sls_file, sls_file_data, indent=2))
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

                        entity = {resource_name: resource}
                        results = cfn_registry.scan(sls_file, entity, skipped_checks, runner_filter)
                        tags = cfn_utils.get_resource_tags(entity, cfn_registry)
                        for check, check_result in results.items():
                            record = Record(check_id=check.id, check_name=check.name, check_result=check_result,
                                            code_block=entity_code_lines, file_path=sls_file,
                                            file_line_range=entity_lines_range,
                                            resource=cf_resource_id, evaluations=variable_evaluations,
                                            check_class=check.__class__.__module__, file_abs_path=file_abs_path, entity_tags=tags)
                            report.add_record(record=record)

            sls_context_parser = SlsContextParser(sls_file, sls_file_data, definitions_raw[sls_file])

            # Sub-sections that have multiple items under them
            for token, registry in MULTI_ITEM_SECTIONS:
                template_items = sls_file_data.get(token)
                if not template_items or not isinstance(template_items, dict):
                    continue
                for item_name, item_content in template_items.items():
                    if not isinstance(item_content, dict_node):
                        continue
                    entity_lines_range, entity_code_lines = sls_context_parser.extract_code_lines(item_content)
                    if entity_lines_range and entity_code_lines:
                        skipped_checks = CfnContextParser.collect_skip_comments(entity_code_lines)
                        variable_evaluations = {}
                        if token == "functions": #nosec
                            # "Enriching" copies things like "environment" and "stackTags" down into the
                            # function data from the provider block since logically that's what serverless
                            # does. This allows checks to see what the complete data would be.
                            sls_context_parser.enrich_function_with_provider(item_name)
                        entity = EntityDetails(sls_context_parser.provider_type, item_content)
                        results = registry.scan(sls_file, entity, skipped_checks, runner_filter)
                        tags = cfn_utils.get_resource_tags(entity, registry)
                        for check, check_result in results.items():
                            record = Record(check_id=check.id, check_name=check.name, check_result=check_result,
                                            code_block=entity_code_lines, file_path=sls_file,
                                            file_line_range=entity_lines_range,
                                            resource=item_name, evaluations=variable_evaluations,
                                            check_class=check.__class__.__module__, file_abs_path=file_abs_path, entity_tags=tags)
                            report.add_record(record=record)
            # Sub-sections that are a single item
            for token, registry in SINGLE_ITEM_SECTIONS:
                item_content = sls_file_data.get(token)
                if not item_content:
                    continue
                entity_lines_range, entity_code_lines = sls_context_parser.extract_code_lines(item_content)
                if not entity_lines_range:
                    entity_lines_range, entity_code_lines = sls_context_parser.extract_code_lines(sls_file_data)

                skipped_checks = CfnContextParser.collect_skip_comments(entity_code_lines)
                variable_evaluations = {}
                entity = EntityDetails(sls_context_parser.provider_type, item_content)
                results = registry.scan(sls_file, entity, skipped_checks, runner_filter)
                tags = cfn_utils.get_resource_tags(entity, registry)
                for check, check_result in results.items():
                    record = Record(check_id=check.id, check_name=check.name, check_result=check_result,
                                    code_block=entity_code_lines, file_path=sls_file,
                                    file_line_range=entity_lines_range,
                                    resource=token, evaluations=variable_evaluations,
                                    check_class=check.__class__.__module__, file_abs_path=file_abs_path, entity_tags=tags)
                    report.add_record(record=record)

            # "Complete" checks
            # NOTE: Ignore code content, no point in showing (could be long)
            entity_lines_range, entity_code_lines = sls_context_parser.extract_code_lines(sls_file_data)
            if entity_lines_range:
                skipped_checks = CfnContextParser.collect_skip_comments(entity_code_lines)
                variable_evaluations = {}
                entity = EntityDetails(sls_context_parser.provider_type, sls_file_data)
                results = complete_registry.scan(sls_file, entity, skipped_checks, runner_filter)
                tags = cfn_utils.get_resource_tags(entity, complete_registry)
                for check, check_result in results.items():
                    record = Record(check_id=check.id, check_name=check.name, check_result=check_result,
                                    code_block=[],              # Don't show, could be large
                                    file_path=sls_file,
                                    file_line_range=entity_lines_range,
                                    resource="complete",        # Weird, not sure what to put where
                                    evaluations=variable_evaluations,
                                    check_class=check.__class__.__module__, file_abs_path=file_abs_path, entity_tags=tags)
                    report.add_record(record=record)

        return report
