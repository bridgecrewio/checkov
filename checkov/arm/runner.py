import logging
import os
from typing import Optional, List, Dict, Tuple

from checkov.arm.registry import arm_resource_registry, arm_parameter_registry
from checkov.arm.parser import parse
from checkov.common.output.record import Record
from checkov.common.output.report import Report, CheckType
from checkov.common.parallelizer.parallel_runner import parallel_runner
from checkov.common.runners.base_runner import BaseRunner, filter_ignored_paths
from checkov.runner_filter import RunnerFilter
from checkov.common.parsers.node import DictNode
from checkov.arm.context_parser import ContextParser

ARM_POSSIBLE_ENDINGS = [".json"]


class Runner(BaseRunner):
    check_type = CheckType.ARM

    def run(
        self,
        root_folder: str,
        external_checks_dir: Optional[List[str]] = None,
        files: Optional[List[str]] = None,
        runner_filter: RunnerFilter = RunnerFilter(),
        collect_skip_comments: bool = True,
    ) -> Report:
        report = Report(self.check_type)
        files_list = []
        filepath_fn = None
        if external_checks_dir:
            for directory in external_checks_dir:
                arm_resource_registry.load_external_checks(directory)

        if files:
            files_list = files.copy()

        if root_folder:
            filepath_fn = lambda f: f'/{os.path.relpath(f, os.path.commonprefix((root_folder, f)))}'
            for root, d_names, f_names in os.walk(root_folder):
                filter_ignored_paths(root, d_names, runner_filter.excluded_paths)
                filter_ignored_paths(root, f_names, runner_filter.excluded_paths)
                for file in f_names:
                    file_ending = os.path.splitext(file)[1]
                    if file_ending in ARM_POSSIBLE_ENDINGS:
                        files_list.append(os.path.join(root, file))

        definitions, definitions_raw = get_files_definitions(files_list, filepath_fn)

        # Filter out empty files that have not been parsed successfully, and filter out non-CF template files
        definitions = {k: v for k, v in definitions.items() if v and v.__contains__("resources")}
        definitions_raw = {k: v for k, v in definitions_raw.items() if k in definitions.keys()}

        for arm_file in definitions.keys():

            # There are a few cases here. If -f was used, there could be a leading / because it's an absolute path,
            # or there will be no leading slash; root_folder will always be none.
            # If -d is used, root_folder will be the value given, and -f will start with a / (hardcoded above).
            # The goal here is simply to get a valid path to the file (which arm_file does not always give).
            if arm_file[0] == '/':
                path_to_convert = (root_folder + arm_file) if root_folder else arm_file
            else:
                path_to_convert = (os.path.join(root_folder, arm_file)) if root_folder else arm_file

            file_abs_path = os.path.abspath(path_to_convert)

            if isinstance(definitions[arm_file], DictNode):
                arm_context_parser = ContextParser(arm_file, definitions[arm_file], definitions_raw[arm_file])
                logging.debug(f"Template Dump for {arm_file}: {definitions[arm_file]}")

                if 'resources' in definitions[arm_file].keys():
                    arm_context_parser.evaluate_default_parameters()

                    # Split out nested resources from base resource
                    for resource in definitions[arm_file]['resources']:
                        if isinstance(resource, dict) and "parent_name" in resource.keys():
                            continue
                        nested_resources = arm_context_parser.search_deep_keys("resources", resource, [])
                        if nested_resources:
                            for nr in nested_resources:
                                nr_element = nr.pop()
                                if nr_element:
                                    for element in nr_element:
                                        new_resource = element
                                        if isinstance(new_resource, dict):
                                            new_resource["parent_name"] = resource.get("name", "")
                                            new_resource["parent_type"] = resource.get("type", "")
                                            definitions[arm_file]['resources'].append(new_resource)

                    for resource in definitions[arm_file]['resources']:
                        resource_id = arm_context_parser.extract_arm_resource_id(resource)
                        report.add_resource(f'{arm_file}:{resource_id}')
                        resource_name = arm_context_parser.extract_arm_resource_name(resource)
                        entity_lines_range, entity_code_lines = arm_context_parser.extract_arm_resource_code_lines(resource)
                        if entity_lines_range and entity_code_lines:
                            # TODO - Variable Eval Message!
                            variable_evaluations = {}

                            skipped_checks = ContextParser.collect_skip_comments(resource)

                            results = arm_resource_registry.scan(arm_file, {resource_name: resource}, skipped_checks,
                                                                 runner_filter)
                            for check, check_result in results.items():
                                record = Record(check_id=check.id, bc_check_id=check.bc_id, check_name=check.name, check_result=check_result,
                                                code_block=entity_code_lines, file_path=arm_file,
                                                file_line_range=entity_lines_range,
                                                resource=resource_id, evaluations=variable_evaluations,
                                                check_class=check.__class__.__module__, file_abs_path=file_abs_path,
                                                severity=check.severity)
                                record.set_guideline(check.guideline)
                                report.add_record(record=record)

                if 'parameters' in definitions[arm_file].keys():
                    parameters = definitions[arm_file]['parameters']
                    for parameter_name, parameter_details in parameters.items():
                        # TODO - Variable Eval Message!
                        variable_evaluations = {}

                        resource_id = f'parameter.{parameter_name}'
                        resource_name = parameter_name
                        entity_lines_range, entity_code_lines = arm_context_parser.extract_arm_resource_code_lines(parameter_details)

                        if entity_lines_range and entity_code_lines:
                            skipped_checks = ContextParser.collect_skip_comments(parameter_details)
                            results = arm_parameter_registry.scan(arm_file, {resource_name: parameter_details}, skipped_checks, runner_filter)
                            for check, check_result in results.items():
                                record = Record(check_id=check.id, bc_check_id=check.bc_id, check_name=check.name, check_result=check_result,
                                                code_block=entity_code_lines, file_path=arm_file,
                                                file_line_range=entity_lines_range,
                                                resource=resource_id, evaluations=variable_evaluations,
                                                check_class=check.__class__.__module__, file_abs_path=file_abs_path,
                                                severity=check.severity)
                                record.set_guideline(check.guideline)
                                report.add_record(record=record)

        return report


def get_files_definitions(files: List[str], filepath_fn=None) \
        -> Tuple[Dict[str, DictNode], Dict[str, List[Tuple[int, str]]]]:
    results = parallel_runner.run_function(lambda f: (f, parse(f)), files)
    definitions = {}
    definitions_raw = {}
    for file, result in results:
        path = filepath_fn(file) if filepath_fn else file
        definitions[path], definitions_raw[path] = result

    return definitions, definitions_raw
