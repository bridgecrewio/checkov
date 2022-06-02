import logging
import os
from typing import Optional, List, Tuple, Dict, Any, Union

import dpath.util

from checkov.cloudformation.checks.resource.base_registry import Registry
from checkov.cloudformation.checks.resource.registry import cfn_registry
from checkov.cloudformation.context_parser import ContextParser, ENDLINE, STARTLINE
from checkov.cloudformation.parser import parse, TemplateSections
from checkov.common.parallelizer.parallel_runner import parallel_runner
from checkov.common.parsers.node import DictNode, ListNode, StrNode
from checkov.common.runners.base_runner import filter_ignored_paths
from checkov.runner_filter import RunnerFilter
from checkov.common.models.consts import YAML_COMMENT_MARK

CF_POSSIBLE_ENDINGS = frozenset([".yml", ".yaml", ".json", ".template"])


def get_resource_tags(entity: Dict[StrNode, DictNode], registry: Registry = cfn_registry) -> Optional[Dict[str, str]]:
    entity_details = registry.extract_entity_details(entity)

    if not entity_details:
        return None

    entity_config = entity_details[-1]

    if not isinstance(entity_config, dict):
        return None

    try:
        properties = entity_config.get("Properties")
        if properties:
            tags = properties.get("Tags")
            if tags:
                return parse_entity_tags(tags)
    except Exception:
        logging.warning(f"Failed to parse tags for entity {entity}")

    return None


def parse_entity_tags(tags: Union[ListNode, Dict[str, Any]]) -> Optional[Dict[str, str]]:
    if isinstance(tags, ListNode):
        tag_dict = {get_entity_value_as_string(tag["Key"]): get_entity_value_as_string(tag["Value"]) for tag in tags}
        return tag_dict
    elif isinstance(tags, dict):
        tag_dict = {
            get_entity_value_as_string(key): get_entity_value_as_string(value)
            for key, value in tags.items()
            if key not in (STARTLINE, ENDLINE)
        }
        return tag_dict
    return None


def get_entity_value_as_string(value: Any) -> str:
    """
    Handles different type of entities with possible CFN function substitutions. Returns the simplest possible string value
    (without performing any function calls).

    Examples:
    Key: Value  # returns simple string

    Key: !Ref ${AWS::AccountId}-data  # returns ${AWS::AccountId}-data

    Key:
    - ${account}-data
    - account: !Ref ${AWS::AccountId}

    # returns ${account}-data

    :param value:
    :return:
    """
    if isinstance(value, dict):
        (function, value) = next(iter(value.items()))
        # If the value is a long-form function, then the first element is the template string (technically str_node)
        # Otherwise the dict value is the template string
        if isinstance(value, list):
            if "Join" in function:
                # Join looks like !Join [, [V1, V2, V3]]
                join_str = str(value[0])
                return join_str.join([str(v) for v in value[1]])
            else:
                return str(value[0])
        else:
            return str(value)
    else:
        return str(value)


def get_folder_definitions(
        root_folder: str, excluded_paths: Optional[List[str]], out_parsing_errors: Dict[str, str] = {}
) -> Tuple[Dict[str, DictNode], Dict[str, List[Tuple[int, str]]]]:
    files_list = []
    for root, d_names, f_names in os.walk(root_folder):
        filter_ignored_paths(root, d_names, excluded_paths)
        filter_ignored_paths(root, f_names, excluded_paths)
        for file in f_names:
            file_ending = os.path.splitext(file)[1]
            if file_ending in CF_POSSIBLE_ENDINGS:
                files_list.append(os.path.join(root, file))

    definitions, definitions_raw = get_files_definitions(files_list, out_parsing_errors)
    return definitions, definitions_raw


def build_definitions_context(
        definitions: Dict[str, DictNode], definitions_raw: Dict[str, List[Tuple[int, str]]]
) -> Dict[str, Dict[str, Any]]:
    definitions_context: Dict[str, Dict[str, Any]] = {}
    # iterate on the files
    for file_path, file_path_definitions in definitions.items():
        # iterate on the definitions (Parameters, Resources, Outputs...)
        for file_path_definition, definition in file_path_definitions.items():
            if (
                    isinstance(file_path_definition, StrNode)
                    and file_path_definition.upper() in TemplateSections.__members__
                    and isinstance(definition, DictNode)
            ):
                # iterate on the actual objects of each definition
                for attribute, attr_value in definition.items():
                    if isinstance(attr_value, DictNode):
                        start_line = attr_value.start_mark.line
                        end_line = attr_value.end_mark.line
                        # fix lines number for yaml and json files
                        first_line_index = 0
                        while not str.strip(definitions_raw[file_path][first_line_index][1]):
                            first_line_index += 1
                        # check if the file is a json file
                        if str.strip(definitions_raw[file_path][first_line_index][1])[0] == "{":
                            start_line += 1
                            end_line += 1
                        else:
                            # add resource comments to definition lines
                            current_line = str.strip(definitions_raw[file_path][start_line - 1][1])
                            while not current_line or current_line[0] == YAML_COMMENT_MARK:
                                start_line -= 1
                                current_line = str.strip(definitions_raw[file_path][start_line - 1][1])

                            # remove next resource comments from definition lines
                            current_line = str.strip(definitions_raw[file_path][end_line - 1][1])
                            while not current_line or current_line[0] == YAML_COMMENT_MARK:
                                end_line -= 1
                                current_line = str.strip(definitions_raw[file_path][end_line - 1][1])

                        code_lines = definitions_raw[file_path][start_line - 1: end_line]
                        dpath.new(
                            definitions_context,
                            [file_path, str(file_path_definition), str(attribute)],
                            {"start_line": start_line, "end_line": end_line, "code_lines": code_lines},
                        )
                        if file_path_definition.upper() == TemplateSections.RESOURCES.value.upper():
                            skipped_checks = ContextParser.collect_skip_comments(
                                entity_code_lines=code_lines,
                                resource_config=attr_value,
                            )
                            dpath.new(
                                definitions_context,
                                [file_path, str(file_path_definition), str(attribute), "skipped_checks"],
                                skipped_checks,
                            )
    return definitions_context


def create_definitions(
        root_folder: str,
        files: Optional[List[str]] = None,
        runner_filter: RunnerFilter = RunnerFilter(),
        out_parsing_errors: Dict[str, str] = {}
) -> Tuple[Dict[str, DictNode], Dict[str, List[Tuple[int, str]]]]:
    definitions = {}
    definitions_raw = {}
    if files:
        files_list = [file for file in files if os.path.splitext(file)[1] in CF_POSSIBLE_ENDINGS]
        definitions, definitions_raw = get_files_definitions(files_list, out_parsing_errors)

    if root_folder:
        definitions, definitions_raw = get_folder_definitions(root_folder, runner_filter.excluded_paths,
                                                              out_parsing_errors)

    return definitions, definitions_raw


def get_files_definitions(files: List[str], out_parsing_errors: Dict[str, str], filepath_fn=None) \
        -> Tuple[Dict[str, DictNode], Dict[str, List[Tuple[int, str]]]]:
    def _parse_file(file):
        parsing_errors = {}
        result = parse(file, parsing_errors)
        return (file, result), parsing_errors

    results = parallel_runner.run_function(_parse_file, files)

    definitions = {}
    definitions_raw = {}
    for result, parsing_errors in results:
        out_parsing_errors.update(parsing_errors)
        (file, parse_result) = result
        path = filepath_fn(file) if filepath_fn else file
        try:
            template, template_lines = parse_result
            if isinstance(template, DictNode) and isinstance(template.get("Resources"), DictNode):
                if validate_properties_in_resources_are_dict(template):
                    definitions[path] = template
                    definitions_raw[path] = template_lines
                else:
                    out_parsing_errors.update({file: 'Resource Properties is not a dictionary'})
            else:
                logging.debug(f"Parsed file {file} incorrectly {template}")
        except (TypeError, ValueError):
            logging.warning(f"CloudFormation skipping {file} as it is not a valid CF template")
            continue

    return definitions, definitions_raw


def validate_properties_in_resources_are_dict(template: DictNode) -> bool:
    template_resources = template.get("Resources")
    for resource_name, resource in template_resources.items():
        if 'Properties' in resource and not isinstance(resource['Properties'], DictNode) or "." in resource_name:
            return False
    return True
