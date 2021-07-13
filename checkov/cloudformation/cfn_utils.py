import logging
import os
from typing import Optional, List

from checkov.cloudformation.checks.resource.registry import cfn_registry
from checkov.cloudformation.parser import parse
from checkov.cloudformation.parser.node import dict_node, list_node
from checkov.common.runners.base_runner import filter_ignored_paths

CF_POSSIBLE_ENDINGS = [".yml", ".yaml", ".json", ".template"]

def get_resource_tags(entity, registry=cfn_registry):
    entity_details = registry.extract_entity_details(entity)

    if not entity_details:
        return None

    entity_config = entity_details[-1]

    if type(entity_config) not in (dict, dict_node):
        return None

    try:
        properties = entity_config.get('Properties')
        if properties:
            tags = properties.get('Tags')
            if tags:
                if type(tags) == list_node:
                    tag_dict = {tag['Key']: str(get_entity_value_as_string(tag['Value'])) for tag in tags}
                    return tag_dict
                elif type(tags) == dict_node:
                    tag_dict = {str(key): str(get_entity_value_as_string(value)) for key, value in tags.items() if key not in ('__startline__', '__endline__')}
                    return tag_dict
    except:
        logging.warning(f'Failed to parse tags for entity {entity}')

    return None


def get_entity_value_as_string(value):
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
    if type(value) in (dict, dict_node):
        (function, value) = list(value.items())[0]
        # If the value is a long-form function, then the first element is the template string (technically str_node)
        # Otherwise the dict value is the template string
        if type(value) == list:
            if 'Join' in function:
                # Join looks like !Join [, [V1, V2, V3]]
                join_str = str(value[0])
                return join_str.join([str(v) for v in value[1]])
            else:
                return value[0]
        else:
            return value
    else:
        return value


def get_folder_definitions(root_folder, excluded_paths: Optional[List[str]]):
    files_list = []
    for root, d_names, f_names in os.walk(root_folder):
        filter_ignored_paths(root, d_names, excluded_paths)
        filter_ignored_paths(root, f_names, excluded_paths)
        for file in f_names:
            file_ending = os.path.splitext(file)[1]
            if file_ending in CF_POSSIBLE_ENDINGS:
                files_list.append(os.path.join(root, file))

    definitions = {}
    definitions_raw = {}
    for file in files_list:
        relative_file_path = f'/{os.path.relpath(file, os.path.commonprefix((root_folder, file)))}'
        try:
            (definitions[relative_file_path], definitions_raw[relative_file_path]) = parse(file)
        except TypeError:
            logging.info(f'CloudFormation skipping {file} as it is not a valid CF template')

    # Filter out empty files that have not been parsed successfully, and filter out non-CF template files
    definitions = {k: v for k, v in definitions.items() if
                   v and isinstance(v, dict_node) and v.__contains__("Resources") and isinstance(v["Resources"],
                                                                                                 dict_node)}
    definitions_raw = {k: v for k, v in definitions_raw.items() if k in definitions.keys()}

    return definitions, definitions_raw

