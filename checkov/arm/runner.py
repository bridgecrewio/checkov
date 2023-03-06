from __future__ import annotations

import logging
import os
from typing import Optional, List, Dict, Tuple

from checkov.arm.registry import arm_resource_registry, arm_parameter_registry
from checkov.arm.parser import parse
from checkov.common.output.extra_resource import ExtraResource
from checkov.common.output.record import Record
from checkov.common.output.report import Report
from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.parallelizer.parallel_runner import parallel_runner
from checkov.common.runners.base_runner import BaseRunner, filter_ignored_paths
from checkov.common.util.secrets import omit_secret_value_from_checks
from checkov.runner_filter import RunnerFilter
from checkov.common.parsers.node import DictNode
from checkov.arm.context_parser import ContextParser

ARM_POSSIBLE_ENDINGS = [".json"]


class Runner(BaseRunner):
    check_type = CheckType.ARM  # noqa: CCE003  # a static attribute

    def __init__(self) -> None:
        super().__init__(file_extensions=ARM_POSSIBLE_ENDINGS)

    def run(
        self,
        root_folder: str,
        external_checks_dir: Optional[List[str]] = None,
        files: Optional[List[str]] = None,
        runner_filter: RunnerFilter | None = None,
        collect_skip_comments: bool = True,
    ) -> Report:
        runner_filter = runner_filter or RunnerFilter()
        if not runner_filter.show_progress_bar:
            self.pbar.turn_off_progress_bar()

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

        self.pbar.initiate(len(definitions))

        for arm_file in definitions.keys():
            self.pbar.set_additional_data({'Current File Scanned': os.path.relpath(arm_file, root_folder)})
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
                                                                 runner_filter, report_type=CheckType.ARM)

                            if results:
                                for check, check_result in results.items():
                                    record = Record(check_id=check.id, bc_check_id=check.bc_id, check_name=check.name, check_result=check_result,
                                                    code_block=entity_code_lines, file_path=arm_file,
                                                    file_line_range=entity_lines_range,
                                                    resource=resource_id, evaluations=variable_evaluations,
                                                    check_class=check.__class__.__module__, file_abs_path=file_abs_path,
                                                    severity=check.severity)
                                    record.set_guideline(check.guideline)
                                    report.add_record(record=record)
                            else:
                                # resources without checks, but not existing ones
                                report.extra_resources.add(
                                    ExtraResource(
                                        file_abs_path=file_abs_path,
                                        file_path=arm_file,
                                        resource=resource_id,
                                    )
                                )

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
                                censored_code_lines = omit_secret_value_from_checks(
                                    check=check,
                                    check_result=check_result,
                                    entity_code_lines=entity_code_lines,
                                    entity_config=parameter_details,
                                    resource_attributes_to_omit=runner_filter.resource_attr_to_omit
                                )
                                record = Record(check_id=check.id, bc_check_id=check.bc_id, check_name=check.name, check_result=check_result,
                                                code_block=censored_code_lines, file_path=arm_file,
                                                file_line_range=entity_lines_range,
                                                resource=resource_id, evaluations=variable_evaluations,
                                                check_class=check.__class__.__module__, file_abs_path=file_abs_path,
                                                severity=check.severity)
                                record.set_guideline(check.guideline)
                                report.add_record(record=record)
            self.pbar.update()
        self.pbar.close()
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
