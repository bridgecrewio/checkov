import json
import os

import jmespath
import logging
import re

import yaml
from yaml import YAMLError

from checkov.cloudformation.parser import cfn_yaml
from checkov.cloudformation.context_parser import ContextParser
from checkov.cloudformation.parser.node import dict_node, str_node

logger = logging.getLogger(__name__)

IAM_ROLE_STATEMENTS_TOKEN = 'iamRoleStatements'
CFN_RESOURCES_TOKEN = 'resources'
PROVIDER_TOKEN = 'provider'
FUNCTIONS_TOKEN = 'functions'
ENVIRONMENT_TOKEN = 'environment'
SUPPORTED_PROVIDERS = ['aws']

# Examples: ${self:myValue,aDefault}
#           ${self:myValue}
SELF_VAR_PATTERN = re.compile(r"\${self:(?P<loc>[\w\-_.]+)(,(?P<default>[\w\-_.]+))?}")
# Examples: ${file(../myCustomFile.yml):myValue,aDefault}
#           ${file(../myCustomFile.yml):myValue}
#           ${file(../myCustomFile.yml)}
FILE_VAR_PATTERN = re.compile(r"\${file\((?P<file>.*)\)(:(?P<loc>[\w\-_.]+)(,(?P<default>[\w\-_.]+))?)?}")

def parse(filename):
    print(f"**** {os.path.dirname(filename)} ****")
    template = None
    template_lines = None
    try:
        (template, template_lines) = cfn_yaml.load(filename)
        if not template or not is_checked_sls_template(template):
            return
    except IOError as e:
        if e.errno == 2:
            logger.error('Template file not found: %s', filename)
            return
        elif e.errno == 21:
            logger.error('Template references a directory, not a file: %s',
                         filename)
            return
        elif e.errno == 13:
            logger.error('Permission denied when accessing template file: %s',
                         filename)
            return
    except UnicodeDecodeError as err:
        logger.error('Cannot read file contents: %s', filename)
        return
    except YAMLError as err:
        return

    process_variables(template, os.path.dirname(filename))

    return template, template_lines


def is_checked_sls_template(template):
    if template.__contains__('provider'):
        # Case provider is a dictionary
        if isinstance(template['provider'], dict_node):
            if template['provider'].get('name').lower() not in SUPPORTED_PROVIDERS:
                return False
        # Case provider is direct provider name
        if isinstance(template['provider'], str_node):
            if template['provider'] not in SUPPORTED_PROVIDERS:
                return False
        if template_contains_cfn_resources(template) or template_contains_key(template, FUNCTIONS_TOKEN):
            return True
    return False


def template_contains_cfn_resources(template):
    if template.__contains__(CFN_RESOURCES_TOKEN):
        if template[CFN_RESOURCES_TOKEN].get('Resources'):
            return True
    return False


def template_contains_key(template, key):
    if ContextParser.search_deep_keys(key, template, []):
        return True
    return False


def process_variables(template, directory):
    """
Modifies the template data in-place to resolve variables.
    """

    # Support for ${file(...):...} variables
    file_data_cache = {}
    process_variables_loop(template, FILE_VAR_PATTERN,
                           lambda d: _file_var_data_lookup(d, file_data_cache, directory))

    # Support for ${self:...} variables
    process_variables_loop(template, SELF_VAR_PATTERN,
                           lambda d: _self_var_data_lookup(d, template))


def process_variables_loop(processing_dict, var_pattern, match_groups_to_value):
    """
Generic processing loop for variables.
    :param processing_dict:                 The dictionary currently being processed. This function will
                                            be called recursively starting at dict provided.
    :param var_pattern:                     A compiled regex pattern which should name match groups
                                            if they are needed for looking up the data source.
    :param match_groups_to_value:           A Callable accepting a dictionary of match groups
                                            (via `groupdict`) and returning a final value to substitute for
                                            the matched portion. If None is returned, the variable will be
                                            left unreplaced.
    """
    # Generic loop for handling a source of key/value tuples (e.g., enumerate() or <dict>.items())
    def process_items(key_value_iterator, data_map):
        for key, value in key_value_iterator():
            if isinstance(value, str):
                altered_value = value
                for match in var_pattern.finditer(value):
                    source_value = match_groups_to_value(match.groupdict())
                    if altered_value == match[0]:           # complete replacement
                        altered_value = source_value
                    else:                                   # partial replacement
                        altered_value = altered_value.replace(match[0], source_value)
                if value != altered_value:
                    data_map[key] = altered_value
                    print(f"Resolved - {key} : {value} -> {altered_value}")
            elif isinstance(value, dict):
                process_variables_loop(value, var_pattern, match_groups_to_value)
            elif isinstance(value, list):
                process_items(lambda: enumerate(value), value)

    process_items(processing_dict.items, processing_dict)


def _load_file_data(file):
    try:
        with open(file, "r") as f:
            if file.endswith(".json"):
                return json.load(f)
            elif file.endswith(".yml") or file.endswith(".yaml"):
                return yaml.safe_load(f)
    except:
        return {}


def _determine_variable_value_from_dict(source_dict, location_str, default):
    if location_str is None:
        return source_dict

    if default is None:
        default = ""
    else:
        default = default.strip()

    # NOTE: String must be quoted to avoid issues with dashes and other reserved
    #       characters. If we just wrap the whole thing, dot separators won't work so:
    #       split and join with individually wrapped tokens.
    #         Original:  foo.bar-baz
    #         Wrapped:   "foo"."bar-baz"
    location = ".".join([f'"{token}"' for token in location_str.split(".")])
    source_value = jmespath.search(location, source_dict)
    if source_value is None:
        source_value = default
    return source_value


def _self_var_data_lookup(group_dict, template):
    location = group_dict["loc"]
    default = group_dict.get("default")
    return _determine_variable_value_from_dict(template, location, default)


def _file_var_data_lookup(group_dict, file_data_cache, directory):
    file = group_dict["file"]

    data = file_data_cache.get(file)
    if data is None:
        data = _load_file_data(os.path.join(directory, file))
        file_data_cache[file] = data

    location = group_dict["loc"]
    default = group_dict.get("default")
    return _determine_variable_value_from_dict(data, location, default)
