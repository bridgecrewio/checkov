import json
import logging
import os
from typing import Optional, List, Tuple, Dict, Any, Union

import dpath.util

from checkov.cloudformation.checks.resource.base_registry import Registry
from checkov.cloudformation.checks.resource.registry import cfn_registry
from checkov.cloudformation.context_parser import ContextParser, ENDLINE, STARTLINE
from checkov.cloudformation.graph_builder.graph_components.block_types import CloudformationTemplateSections
from checkov.cloudformation.parser import parse
from checkov.cloudformation.parser.node import dict_node, list_node, str_node
from checkov.common.runners.base_runner import filter_ignored_paths
from checkov.runner_filter import RunnerFilter
from checkov.common.models.consts import YAML_COMMENT_MARK

CF_POSSIBLE_ENDINGS = frozenset([".yml", ".yaml", ".json", ".template"])


def get_resource_tags(entity: Dict[str_node, dict_node], registry: Registry = cfn_registry) -> Optional[Dict[str, str]]:
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
    except:
        logging.warning(f"Failed to parse tags for entity {entity}")

    return None


def parse_entity_tags(tags: Union[list_node, Dict[str, Any]]) -> Optional[Dict[str, str]]:
    if isinstance(tags, list_node):
        tag_dict = {tag["Key"]: get_entity_value_as_string(tag["Value"]) for tag in tags}
        return tag_dict
    elif isinstance(tags, dict):
        tag_dict = {
            str(key): get_entity_value_as_string(value)
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
    root_folder: str, excluded_paths: Optional[List[str]]
) -> Tuple[Dict[str, dict_node], Dict[str, List[Tuple[int, str]]]]:
    files_list = []
    for root, d_names, f_names in os.walk(root_folder):
        filter_ignored_paths(root, d_names, excluded_paths)
        filter_ignored_paths(root, f_names, excluded_paths)
        for file in f_names:
            file_ending = os.path.splitext(file)[1]
            if file_ending in CF_POSSIBLE_ENDINGS:
                files_list.append(os.path.join(root, file))

    definitions: Dict[str, dict_node] = {}
    definitions_raw: Dict[str, List[Tuple[int, str]]] = {}
    for file in files_list:
        relative_file_path = f"/{os.path.relpath(file, os.path.commonprefix((root_folder, file)))}"
        try:
            template, template_lines = parse(file)
            if isinstance(template, dict_node) and isinstance(template.get("Resources"), dict_node):
                definitions[relative_file_path] = template
                definitions_raw[relative_file_path] = template_lines
            else:
                logging.debug(f"Parsed file {file} incorrectly {template}")
        except (TypeError, ValueError) as e:
            logging.warning(f"CloudFormation skipping {file} as it is not a valid CF template\n{e}")
            continue

    definitions = {create_file_abs_path(root_folder, file_path): v for (file_path, v) in definitions.items()}
    definitions_raw = {create_file_abs_path(root_folder, file_path): v for (file_path, v) in definitions_raw.items()}

    return definitions, definitions_raw


def build_definitions_context(
    definitions: Dict[str, dict_node], definitions_raw: Dict[str, List[Tuple[int, str]]], root_folder: str
) -> Dict[str, Dict[str, Any]]:
    definitions_context: Dict[str, Dict[str, Any]] = {}
    # iterate on the files
    for file_path, file_path_definitions in definitions.items():
        # iterate on the definitions (Parameters, Resources, Outputs...)
        for file_path_definition, definition in file_path_definitions.items():
            if (
                isinstance(file_path_definition, str_node)
                and file_path_definition.upper() in CloudformationTemplateSections.__members__
                and isinstance(definition, dict_node)
            ):
                # iterate on the actual objects of each definition
                for attribute, attr_value in definition.items():
                    if isinstance(attr_value, dict_node):
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
                            current_line = str.strip(definitions_raw[file_path][start_line - 1][1])
                            while not current_line or current_line[0] == YAML_COMMENT_MARK:
                                start_line -= 1
                                current_line = str.strip(definitions_raw[file_path][start_line - 1][1])
                            current_line = str.strip(definitions_raw[file_path][end_line - 1][1])
                            while not current_line or current_line[0] == YAML_COMMENT_MARK:
                                end_line -= 1
                                current_line = str.strip(definitions_raw[file_path][end_line - 1][1])

                        code_lines = definitions_raw[file_path][start_line - 1 : end_line]
                        dpath.new(
                            definitions_context,
                            [file_path, str(file_path_definition), str(attribute)],
                            {"start_line": start_line, "end_line": end_line, "code_lines": code_lines},
                        )
                        if file_path_definition.upper() == CloudformationTemplateSections.RESOURCES.value.upper():
                            skipped_checks = ContextParser.collect_skip_comments(code_lines)
                            dpath.new(
                                definitions_context,
                                [file_path, str(file_path_definition), str(attribute), "skipped_checks"],
                                skipped_checks,
                            )
    return definitions_context


def create_file_abs_path(root_folder: str, cf_file: str) -> str:
    # There are a few cases here. If -f was used, there could be a leading / because it's an absolute path,
    # or there will be no leading slash; root_folder will always be none.
    # If -d is used, root_folder will be the value given, and -f will start with a / (hardcoded above).
    # The goal here is simply to get a valid path to the file (which cf_file does not always give).
    if cf_file.startswith("/"):
        path_to_convert = (root_folder + cf_file) if root_folder else cf_file
    else:
        path_to_convert = (os.path.join(root_folder, cf_file)) if root_folder else cf_file

    return os.path.abspath(path_to_convert)


def create_definitions(
    root_folder: str, files: Optional[List[str]] = None, runner_filter: RunnerFilter = RunnerFilter()
) -> Tuple[Dict[str, dict_node], Dict[str, List[Tuple[int, str]]]]:
    definitions = {}
    definitions_raw = {}
    if files:
        for file in files:
            (definitions[file], definitions_raw[file]) = parse(file)

    if root_folder:
        definitions, definitions_raw = get_folder_definitions(root_folder, runner_filter.excluded_paths)

        # Filter out empty files that have not been parsed successfully, and filter out non-CF template files
    definitions = {
        k: v
        for k, v in definitions.items()
        if v and isinstance(v, dict_node) and v.__contains__("Resources") and isinstance(v["Resources"], dict_node)
    }
    definitions_raw = {k: v for k, v in definitions_raw.items() if k in definitions.keys()}

    for cf_file in definitions.keys():
        cf_context_parser = ContextParser(cf_file, definitions[cf_file], definitions_raw[cf_file])
        logging.debug(
            "Template Dump for {}: {}".format(cf_file, json.dumps(definitions[cf_file], indent=2, default=str))
        )
        cf_context_parser.evaluate_default_refs()
    return definitions, definitions_raw
