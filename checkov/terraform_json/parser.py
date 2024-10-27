from __future__ import annotations

import itertools
import logging
from pathlib import Path
from typing import Any

from yaml.scanner import ScannerError
from yaml import YAMLError

from checkov.common.parsers.json import parse as json_parse
from checkov.common.parsers.yaml import loader
from checkov.common.resource_code_logger_filter import add_resource_code_filter_to_logger
from checkov.common.util.consts import LINE_FIELD_NAMES
from checkov.common.util.file_utils import read_file_with_any_encoding
from checkov.terraform.graph_builder.graph_components.block_types import BlockType

COMMENT_FIELD_NAME = "//"
IGNORE_FILED_NAMES = {COMMENT_FIELD_NAME} | LINE_FIELD_NAMES
SIMPLE_TYPES = (str, int, float, bool)

logger = logging.getLogger(__name__)
add_resource_code_filter_to_logger(logger)


def parse(file_path: Path) -> tuple[dict[str, Any], list[tuple[int, str]]] | tuple[None, None]:
    """Parse file to dict object"""

    template = None
    template_lines = None
    try:
        template, template_lines = loads(file_path=file_path)
    except IOError as e:
        if e.errno == 2:
            logger.error(f"Template file not found: {file_path}")
        elif e.errno == 21:
            logger.error(f"Template references a directory, not a file: {file_path}")
        elif e.errno == 13:
            logger.error(f"Permission denied when accessing template file: {file_path}")
    except UnicodeDecodeError:
        logger.error(f"Cannot read file contents: {file_path}")
    except ScannerError as err:
        if err.problem in ("found character '\\t' that cannot start any token", "found unknown escape character"):
            try:
                result = json_parse(file_path, allow_nulls=False)
                if result:
                    template, template_lines = result  # type:ignore[assignment]  # this is handled by the next line
                    if isinstance(template, list):
                        # should not happen and is more relevant for type safety
                        template = template[0]
            except Exception:
                logger.error(f"Template {file_path} is malformed: {err.problem}")
                logger.error(f"Tried to parse {file_path} as JSON", exc_info=True)
    except YAMLError:
        pass

    if template is None or template_lines is None:
        return None, None

    return template, template_lines


def loads(file_path: Path) -> tuple[dict[str, Any], list[tuple[int, str]]]:
    """Loads the given JSON file with line numbers"""

    content = read_file_with_any_encoding(file_path=file_path)

    file_lines = [(idx + 1, line) for idx, line in enumerate(content.splitlines(keepends=True))]

    template: "dict[str, Any] | list[dict[str, Any]]" = loader.loads(content=content)
    if not template:
        template = {}
    if isinstance(template, list):
        template = template[0]

    if template:
        template = prepare_definition(template)

    return template, file_lines


def prepare_definition(definition: dict[str, Any]) -> dict[str, Any]:
    definition_new: dict[str, Any] = {}

    for block_type, blocks in definition.items():
        if block_type == COMMENT_FIELD_NAME or block_type in LINE_FIELD_NAMES:
            continue

        definition_new[block_type] = handle_block_type(block_type=block_type, blocks=blocks)

    return definition_new


def handle_block_type(block_type: str, blocks: dict[str, Any]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []

    for block_name, config in blocks.items():
        if block_name == COMMENT_FIELD_NAME or block_name in LINE_FIELD_NAMES:
            continue

        if block_type in (BlockType.RESOURCE, BlockType.DATA):
            # data/resource have an extra nested level resource_type -> resource_name -> resource_config
            for resource_name, resource_config in config.items():
                if resource_name in IGNORE_FILED_NAMES:
                    continue
                result.append({block_name: {resource_name: hclify(obj=resource_config)}})
        elif block_type == BlockType.PROVIDER:
            # provider are stored as a list, which we need to move one level higher to add the name
            for provider_config in config:
                result.append({block_name: hclify(obj=provider_config)})
        elif block_type == BlockType.LOCALS:
            # a local block is stored as single dict
            return [hclify(obj=blocks)]
        else:
            result.append({block_name: hclify(obj=config)})

    return result


def hclify(
    obj: dict[str, Any],
    conf: dict[str, Any] | None = None,
    parent_key: str | None = None,
) -> dict[str, list[Any]]:
    ret_dict = {}

    if not isinstance(obj, dict):
        raise Exception("this method receives only dicts")

    for key, value in obj.items():
        if key == COMMENT_FIELD_NAME:
            # don't hclify the comment block
            ret_dict[key] = value
        elif _is_simple_type(value) or _is_list_of_simple_types(value):
            if key in IGNORE_FILED_NAMES:
                ret_dict[key] = value
            elif parent_key == "tags":
                ret_dict[key] = value
            else:
                ret_dict[key] = _clean_simple_type_list([value])
        elif _is_list_of_dicts(value):
            child_list = []
            conf_val = conf.get(key, []) if conf else []
            if not isinstance(conf_val, list):
                # this occurs, when a resource in the current state has no value for that argument
                conf_val = [conf_val]

            for internal_val, internal_conf_val in itertools.zip_longest(value, conf_val):
                if isinstance(internal_val, dict):
                    child_list.append(hclify(internal_val, internal_conf_val, parent_key=key))
            if key == "tags":
                ret_dict[key] = [child_list]
            else:
                ret_dict[key] = child_list
        elif isinstance(value, dict):
            child_dict = hclify(value, parent_key=key)
            if parent_key == "tags":
                ret_dict[key] = child_dict
            else:
                ret_dict[key] = [child_dict]

    return ret_dict


def _is_simple_type(obj: Any) -> bool:
    if obj is None:
        return True
    if isinstance(obj, SIMPLE_TYPES):
        return True
    return False


def _is_list_of_simple_types(obj: Any) -> bool:
    if not isinstance(obj, list):
        return False
    for i in obj:
        if not _is_simple_type(i):
            return False
    return True


def _is_list_of_dicts(obj: Any) -> bool:
    if not isinstance(obj, list):
        return False
    for i in obj:
        if isinstance(i, dict):
            return True
    return False


def _clean_simple_type_list(value_list: list[Any]) -> list[Any]:
    """
    Given a list of simple types return a cleaned list of simple types.
    Converts booleans that are input as strings back to booleans to maintain consistent expectations for later evaluation.
    Sometimes Terraform Plan will output Map values as strings regardless of boolean input.
    """
    for i in range(len(value_list)):
        if isinstance(value_list[i], str):
            lower_case_value = value_list[i].lower()
            if lower_case_value == "true":
                value_list[i] = True
            if lower_case_value == "false":
                value_list[i] = False
    return value_list
