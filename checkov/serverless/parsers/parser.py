from __future__ import annotations

import json
import os
from collections.abc import Iterable
from pathlib import Path
from typing import Tuple, Optional, List, Any, Pattern, Callable

import jmespath
import logging
import re

import yaml
from yaml import YAMLError

from checkov.cloudformation.parser import cfn_yaml
from checkov.cloudformation.context_parser import ContextParser
from checkov.cloudformation.parser.cfn_yaml import CfnParseError
from checkov.common.models.consts import SLS_DEFAULT_VAR_PATTERN
from checkov.common.parsers.node import DictNode, StrNode
from checkov.common.resource_code_logger_filter import add_resource_code_filter_to_logger

logger = logging.getLogger(__name__)
add_resource_code_filter_to_logger(logger)

IAM_ROLE_STATEMENTS_TOKEN = 'iamRoleStatements'  # nosec
CFN_RESOURCES_TOKEN = 'resources'  # nosec
PROVIDER_TOKEN = 'provider'  # nosec
FUNCTIONS_TOKEN = 'functions'  # nosec
ENVIRONMENT_TOKEN = 'environment'  # nosec
STACK_TAGS_TOKEN = 'stackTags'  # nosec
TAGS_TOKEN = 'tags'  # nosec
SUPPORTED_PROVIDERS = ['aws']

QUOTED_WORD_SYNTAX = re.compile(r"(?:('|\").*?\1)")
FILE_LOCATION_PATTERN = re.compile(r'^file\(([^?%*:|"<>]+?)\)')


def parse(filename: str) -> tuple[dict[str, Any], list[tuple[int, str]]] | None:
    template = None
    template_lines = None
    try:
        (template, template_lines) = cfn_yaml.load(filename, cfn_yaml.ContentType.SLS)
        if not template or not is_checked_sls_template(template):
            return None
    except IOError as e:
        if e.errno == 2:
            logger.error('Template file not found: %s', filename)
            return None
        elif e.errno == 21:
            logger.error('Template references a directory, not a file: %s',
                         filename)
            return None
        elif e.errno == 13:
            logger.error('Permission denied when accessing template file: %s',
                         filename)
            return None
    except UnicodeDecodeError:
        logger.error('Cannot read file contents: %s', filename)
        return None
    except CfnParseError:
        logger.warning(f"Failed to parse file {filename} because it isn't a valid template")
        return None
    except YAMLError:
        logger.warning(f"Failed to parse file {filename} as a yaml")
        return None

    if template is None or template_lines is None:
        return None

    process_variables(template, filename)

    return template, template_lines


def is_checked_sls_template(template: dict[str, Any]) -> bool:
    if template.__contains__('provider'):
        # Case provider is a dictionary
        if isinstance(template['provider'], DictNode):
            if template['provider'].get('name', '').lower() not in SUPPORTED_PROVIDERS:
                return False
        # Case provider is direct provider name
        if isinstance(template['provider'], StrNode):
            if template['provider'] not in SUPPORTED_PROVIDERS:
                return False
        return True
    return False


def template_contains_cfn_resources(template: dict[str, Any]) -> bool:
    if template.__contains__(CFN_RESOURCES_TOKEN) and isinstance(template[CFN_RESOURCES_TOKEN], DictNode):
        if template[CFN_RESOURCES_TOKEN].get('Resources'):
            return True
    return False


def template_contains_key(template: dict[str, Any], key: str) -> bool:
    if ContextParser.search_deep_keys(key, template, []):
        return True
    return False


def process_variables(template: dict[str, Any], filename: str) -> dict[str, Any]:
    """
Modifies the template data in-place to resolve variables.
    """

    file_data_cache: dict[str, dict[str, Any]] = {}
    service_file_directory = os.path.dirname(filename)

    var_pattern = jmespath.search("provider.variableSyntax", template)
    if var_pattern is not None:
        # Remove to prevent self-matching during processing
        del template["provider"]["variableSyntax"]
    else:
        var_pattern = SLS_DEFAULT_VAR_PATTERN
    compiled_var_pattern = re.compile(var_pattern)

    # Processing is done in a loop to deal with chained references and the like.
    # Loop while the data is being changed, stop when no more changes are happening.
    # To ensure there's not some kind of oscillation, a cap of 25 passes is in place.
    # More than a couple loops isn't normally expected.
    # NOTE: If this approach proves to be a performance liability, a DAG will be needed.
    loop_count = 0
    for _ in range(0, 25):
        loop_count += 1
        made_change = False

        if process_variables_loop(template, compiled_var_pattern,
                                  # vt = var type
                                  # vl = var location
                                  # ft = fallback var type
                                  # fl = fallback var location
                                  lambda vt, vl, ft, fl: _load_var_data(vt, vl, ft, fl,
                                                                        file_data_cache,
                                                                        template, service_file_directory)):
            made_change = True

        if not made_change:
            break
    logger.debug("Processing of %s variables took %d loop iterations", filename, loop_count)

    return template


def process_variables_loop(
    template: dict[str, Any],
    var_pattern: Pattern[str],
    param_lookup_function: Callable[[str | None, str | None, str | None, str | None], Any],
) -> bool:
    """
Generic processing loop for variables.
    :param template:                The dictionary currently being processed. This function will
                                    be called recursively starting at dict provided.
    :param var_pattern:             A compiled regex pattern which should name match groups
                                    if they are needed for looking up the data source.
    :param param_lookup_function:   A Callable taking four arguments:
                                    1) the type (e.g., "self", "file(/path/to/file.yml)")
                                    2) the location (e.g., "custom.my_property")
                                    3) fallback var type (same as above plus None for static value)
                                    4) fallback var location or value if type was None
    """
    # Generic loop for handling a source of key/value tuples (e.g., enumerate() or <dict>.items())
    def process_items_helper(key_value_iterator: Iterable[tuple[str, Any]], data_map: dict[str, Any]) -> bool:
        made_change = False
        for key, value in key_value_iterator:
            if isinstance(value, str):
                altered_value = value
                for match in var_pattern.finditer(value):
                    parsed_var = _parse_var(match[1])
                    if parsed_var is None:
                        continue

                    var_type, var_loc, fallback_type, fallback_loc = parsed_var
                    source_value = param_lookup_function(var_type, var_loc, fallback_type, fallback_loc)

                    # If we can't find a value, skip it
                    if source_value is None:
                        continue
                    try:
                        if altered_value == match[0]:           # complete replacement
                            altered_value = source_value
                        else:                                   # partial replacement

                            altered_value = altered_value.replace(match[0], source_value)
                    except TypeError:
                        pass
                if value != altered_value:
                    data_map[key] = altered_value
                    made_change = True
            elif isinstance(value, dict):
                if process_variables_loop(value, var_pattern, param_lookup_function):
                    made_change = True
            elif isinstance(value, list):
                if process_items_helper(enumerate(value), value):  # type:ignore[arg-type]
                    made_change = True
        return made_change

    return process_items_helper(template.items(), template)


def _load_var_data(
    var_type: str | None,
    var_location: str | None,
    fallback_var_type: str | None,
    fallback_var_location: str | None,
    file_cache: dict[str, dict[str, Any]],
    self_data_source: dict[str, Any],
    service_file_directory: str,
) -> Any:
    """
Load data based on the type/path (see param_lookup_function parameter of process_variables for more info).

    :param var_type:        Either the type of the variable (see process_variables function) or None to
                            indicate that var_location is a raw value.
    :param var_location:    Either the location of the variable (see process_variables function) or a
                            raw value if var_type is None

    :return     None if the variable could not be resolved
    """
    value = None
    if var_type is None:
        value = var_location
    elif var_type == "self":
        value = _determine_variable_value_from_dict(self_data_source, var_location, None)
    elif var_type == "env":
        value = _determine_variable_value_from_dict(dict(os.environ.items()), var_location, None)
    elif var_type.startswith("file("):
        match = FILE_LOCATION_PATTERN.match(var_type)
        if match is None:
            return None
        data_source = _load_file_data(match[1], file_cache, service_file_directory)
        value = _determine_variable_value_from_dict(data_source, var_location, None)

    if value is None and fallback_var_location is not None:
        return _load_var_data(fallback_var_type, fallback_var_location, None, None,
                              file_cache, self_data_source, service_file_directory)
    return value


def _determine_variable_value_from_dict(
    source_dict: dict[str, Any], location_str: str | None, default: str | None
) -> Any:
    if location_str is None:
        return source_dict

    if default is not None:
        default = default.strip()

    # NOTE: String must be quoted to avoid issues with dashes and other reserved
    #       characters. If we just wrap the whole thing, dot separators won't work so:
    #       split and join with individually wrapped tokens.
    #         Original:  foo.bar-baz
    #         Wrapped:   "foo"."bar-baz"
    location = ".".join([f'"{token}"' for token in location_str.split(".")])
    source_value = jmespath.search(location, source_dict)
    if source_value is None:
        return default
    return source_value


def _self_var_data_lookup(group_dict: dict[str, Any], template: dict[str, Any]) -> Any:
    location = group_dict["loc"]
    default = group_dict.get("default")
    return _determine_variable_value_from_dict(template, location, default)


def _load_file_data(
    file_location: str, file_data_cache: dict[str, dict[str, Any]], service_file_directory: str
) -> dict[str, Any]:
    file_location = file_location.replace("~", str(Path.home()))
    file_location = file_location if os.path.isabs(file_location) else \
        os.path.join(service_file_directory, file_location)

    data = file_data_cache.get(file_location)
    if data is None:
        try:
            with open(file_location, "r") as f:
                if file_location.endswith(".json"):
                    data = json.load(f)
                elif file_location.endswith(".yml") or file_location.endswith(".yaml"):
                    data = yaml.safe_load(f)
        except Exception:
            data = {}
        file_data_cache[file_location] = data or {}
    return data or {}


def _token_to_type_and_loc(token: str) -> Tuple[Optional[str], Optional[str]]:
    file_match = FILE_LOCATION_PATTERN.match(token)
    if file_match is not None:
        if ":" not in token:
            return file_match[0], None

        return file_match[0].strip(), token[len(file_match[0]) + 1 :].strip()  # +1 for colon

    if ":" not in token:
        return None, token

    index = token.index(":")
    return token[:index].strip(), token[index + 1 :].strip()


def _parse_var(var_str: str) -> tuple[str | None, str | None, str | None, str | None] | None:
    """
Returns a tuple of the var type, var loc, fallback type and fallback loc. See docs for the
param_lookup_function parameter of process_variables_loop for more info.
    """
    tokens = _tokenize_by_commas(var_str.strip())
    if not tokens:
        return None

    var_type, var_loc = _token_to_type_and_loc(tokens[0])

    if len(tokens) > 1:
        fallback_type, fallback_loc = _token_to_type_and_loc(tokens[1])
    else:
        fallback_type = None
        fallback_loc = None

    return var_type, var_loc, fallback_type, fallback_loc


def _tokenize_by_commas(string: str) -> Optional[List[str]]:
    """
    Tokenize the given value by commas, respecting quoted blocks.
    """
    if not string:
        return None

    quoted_comma_ranges = [range(m.start(0), m.end(0)) for m in QUOTED_WORD_SYNTAX.finditer(string)]

    def clean(s: str) -> str:
        s = s.strip()  # whitespace
        if len(s) > 0 and s[0] == '"' and s[len(s) - 1] == '"':  # surrounding quotes
            s = s[1:-1]
        if len(s) > 0 and s[0] == "'" and s[len(s) - 1] == "'":
            s = s[1:-1]
        return s

    block_start_index = 0
    search_start_index = block_start_index
    tokens = []
    index = string.find(",", search_start_index)
    while index > 0:
        is_quoted = False
        for quoted_comma_range in quoted_comma_ranges:
            if index in quoted_comma_range:
                is_quoted = True
                break
        if is_quoted:
            search_start_index = index + 1
        else:
            tokens.append(clean(string[block_start_index:index]))
            block_start_index = index + 1
            search_start_index = block_start_index
        index = string.find(",", search_start_index)

    if block_start_index < len(string):
        tokens.append(clean(string[block_start_index:]))
    return tokens
