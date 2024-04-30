from __future__ import annotations

import json
import logging
import os
from collections.abc import Sequence
from typing import Any, TYPE_CHECKING, TypeVar, cast, Tuple

from lark import Tree
import re

from checkov.common.typing import TFDefinitionKeyType
from checkov.common.util.consts import DEFAULT_EXTERNAL_MODULES_DIR
from checkov.common.util.data_structures_utils import pickle_deepcopy
from checkov.common.util.json_utils import CustomJSONEncoder, object_hook
from checkov.terraform.modules.module_objects import TFDefinitionKey
from checkov.terraform.checks.utils.dependency_path_handler import unify_dependency_path
from checkov.terraform.graph_builder.utils import remove_module_dependency_in_path
from checkov.common.util.parser_utils import TERRAFORM_NESTED_MODULE_PATH_PREFIX, TERRAFORM_NESTED_MODULE_PATH_ENDING

if TYPE_CHECKING:
    from typing_extensions import TypeAlias

_Conf = TypeVar("_Conf", bound="dict[Any, Any]")

ENTITY_NAME_PATTERN = re.compile(r"[^\W0-9][\w-]*")
RESOLVED_MODULE_PATTERN = re.compile(r"\[.+\#.+\]")
_Hcl2Payload: TypeAlias = "dict[str, list[dict[str, Any]]]"
external_modules_download_path = os.environ.get('EXTERNAL_MODULES_DIR', DEFAULT_EXTERNAL_MODULES_DIR)


def is_valid_block(block: Any) -> bool:
    if not isinstance(block, dict):
        return True

    # if the block is empty, there's no need to process it further
    if not block:
        return False

    entity_name = next(iter(block.keys()))
    if re.fullmatch(ENTITY_NAME_PATTERN, entity_name):
        return True
    return False


def validate_malformed_definitions(raw_data: _Hcl2Payload) -> _Hcl2Payload:
    return {
        block_type: [block for block in blocks if is_valid_block(block)]
        for block_type, blocks in raw_data.items()
    }


def clean_bad_definitions(tf_definition_list: _Hcl2Payload) -> _Hcl2Payload:
    return {
        block_type: [
            definition
            for definition in definition_list
            if block_type in {"locals", "terraform"} or not isinstance(definition, dict) or len(definition) == 1
        ]
        for block_type, definition_list in tf_definition_list.items()
    }


def safe_index(sequence_hopefully: Sequence[Any], index: int) -> Any:
    try:
        return sequence_hopefully[index]
    except IndexError:
        logging.debug(f'Failed to parse index int ({index}) out of {sequence_hopefully}', exc_info=True)
        return None


def remove_module_dependency_from_path(path: str) -> str:
    """
    :param path: path that looks like "dir/main.tf[other_dir/x.tf#0]
    :return: only the outer path: dir/main.tf
    """
    if "#" in path:
        path = re.sub(RESOLVED_MODULE_PATTERN, '', path)
    return path


def get_module_dependency_map(
    tf_definitions: dict[str, Any]
) -> tuple[dict[str, list[list[str]]], dict[str, Any], dict[tuple[str, str], list[str]]]:
    """
    :param tf_definitions, with paths in format 'dir/main.tf[module_dir/main.tf#0]'
    :return module_dependency_map: mapping between directories and the location of its module definition:
            {'dir': 'module_dir/main.tf'}
    :return tf_definitions: with paths in format 'dir/main.tf'
    """
    module_dependency_map: dict[str, list[list[str]]] = {}
    copy_of_tf_definitions = {}
    dep_index_mapping: dict[tuple[str, str], list[str]] = {}
    origin_keys = list(filter(lambda k: not k.endswith(TERRAFORM_NESTED_MODULE_PATH_ENDING), tf_definitions.keys()))
    unevaluated_keys = list(filter(lambda k: k.endswith(TERRAFORM_NESTED_MODULE_PATH_ENDING), tf_definitions.keys()))
    for file_path in origin_keys:
        dir_name = os.path.dirname(file_path)
        module_dependency_map[dir_name] = [[]]
        copy_of_tf_definitions[file_path] = pickle_deepcopy(tf_definitions[file_path])

    next_level, unevaluated_keys = get_next_vertices(origin_keys, unevaluated_keys)
    while next_level:
        for file_path in next_level:
            path, module_dependency, module_dependency_num = remove_module_dependency_in_path(file_path)
            dir_name = os.path.dirname(path)
            current_deps = pickle_deepcopy(module_dependency_map[os.path.dirname(module_dependency)])
            for dep in current_deps:
                dep.append(module_dependency)
            if dir_name not in module_dependency_map:
                module_dependency_map[dir_name] = current_deps
            else:
                for dep in current_deps:
                    if dep not in module_dependency_map[dir_name]:
                        module_dependency_map[dir_name].append(dep)
            copy_of_tf_definitions[path] = pickle_deepcopy(tf_definitions[file_path])
            origin_keys.append(path)
            dep_index_mapping.setdefault((path, module_dependency), []).append(module_dependency_num)
        next_level, unevaluated_keys = get_next_vertices(origin_keys, unevaluated_keys)
    for key, dep_trails in module_dependency_map.items():
        hashes = set()
        deduped = []
        for trail in dep_trails:
            trail_hash = unify_dependency_path(trail)
            if trail_hash in hashes:
                continue
            hashes.add(trail_hash)
            deduped.append(trail)
        module_dependency_map[key] = deduped
    return module_dependency_map, copy_of_tf_definitions, dep_index_mapping


def get_next_vertices(evaluated_files: list[str], unevaluated_files: list[str]) -> tuple[list[str], list[str]]:
    """
    This function implements a lazy separation of levels for the evaluated files. It receives the evaluated
    files, and returns 2 lists:
    1. The next level of files - files from the unevaluated_files which have no unresolved dependency (either
        no dependency or all dependencies were evaluated).
    2. unevaluated - files which have yet to be evaluated, and still have pending dependencies

    Let's say we have this dependency tree:
    a -> b
    x -> b
    y -> c
    z -> b
    b -> c
    c -> d

    The first run will return [a, y, x, z] as the next level since all of them have no dependencies
    The second run with the evaluated being [a, y, x, z] will return [b] as the next level.
    Please mind that [c] has some resolved dependencies (from y), but has unresolved dependencies from [b].
    The third run will return [c], and the fourth will return [d].
    """

    next_level, unevaluated, do_not_eval_yet = [], [], []
    for key in unevaluated_files:
        found = False
        for eval_key in evaluated_files:
            if eval_key in key:
                found = True
                break
        if not found:
            do_not_eval_yet.append(key.split(TERRAFORM_NESTED_MODULE_PATH_PREFIX)[0])
            unevaluated.append(key)
        else:
            next_level.append(key)

    move_to_uneval = list(filter(lambda k: k.split(TERRAFORM_NESTED_MODULE_PATH_PREFIX)[0] in do_not_eval_yet, next_level))
    for k in move_to_uneval:
        next_level.remove(k)
        unevaluated.append(k)
    return next_level, unevaluated


def clean_parser_types(conf: _Conf) -> _Conf:
    if not conf:
        return conf

    sorted_keys = list(conf.keys())
    first_key_type = type(sorted_keys[0])
    if first_key_type is None:
        return {}

    if all(isinstance(x, first_key_type) for x in sorted_keys):
        sorted_keys.sort()

    # Create a new dict where the keys are sorted alphabetically
    sorted_conf = {key: conf[key] for key in sorted_keys}
    for attribute, values in sorted_conf.items():
        if attribute == 'alias':
            continue
        if isinstance(values, list):
            sorted_conf[attribute] = clean_parser_types_lst(values)
        elif isinstance(values, dict):
            sorted_conf[attribute] = clean_parser_types(values)
        elif isinstance(values, str) and values in ('true', 'false'):
            sorted_conf[attribute] = True if values == 'true' else False
        elif isinstance(values, set):
            sorted_conf[attribute] = clean_parser_types_lst(list(values))
        elif isinstance(values, Tree):
            sorted_conf[attribute] = str(values)
    return sorted_conf  # type:ignore[return-value]  # still the same type as before


def clean_parser_types_lst(values: list[Any]) -> list[Any]:
    for idx, val in enumerate(values):
        if isinstance(val, dict):
            values[idx] = clean_parser_types(val)
        elif isinstance(val, list):
            values[idx] = clean_parser_types_lst(val)
        elif isinstance(val, str):
            if val == 'true':
                values[idx] = True
            elif val == 'false':
                values[idx] = False
        elif isinstance(val, set):
            values[idx] = clean_parser_types_lst(list(val))
    str_values_in_lst = []
    result_values = []
    for val in values:
        if isinstance(val, str):
            str_values_in_lst.append(val)
        else:
            result_values.append(val)
    str_values_in_lst.sort()
    result_values.extend(str_values_in_lst)
    return result_values


def serialize_definitions(tf_definitions: _Conf) -> _Conf:
    return cast("_Conf", json.loads(json.dumps(tf_definitions, cls=CustomJSONEncoder), object_hook=object_hook))


def get_module_from_full_path(file_path: TFDefinitionKey | None) -> Tuple[TFDefinitionKey | None, None]:
    if not file_path or not is_nested(file_path):
        return None, None
    if file_path.tf_source_modules is None:
        return None, None
    return TFDefinitionKey(file_path=file_path.tf_source_modules.path, tf_source_modules=file_path.tf_source_modules.nested_tf_module), None


def get_module_name(file_path: TFDefinitionKey) -> str | None:
    if not file_path.tf_source_modules:
        return None
    module_name = file_path.tf_source_modules.name
    if isinstance(file_path.tf_source_modules.foreach_idx, int) or file_path.tf_source_modules.foreach_idx:
        foreach_or_count = '"' if isinstance(file_path.tf_source_modules.foreach_idx, str) else ''
        module_name = f'{module_name}[{foreach_or_count}{file_path.tf_source_modules.foreach_idx}{foreach_or_count}]'
    return module_name


def is_nested(full_path: TFDefinitionKey | None) -> bool:
    return full_path.tf_source_modules is not None if full_path is not None else False


def get_abs_path(file_path: TFDefinitionKeyType) -> str:
    # file_path might be str for terraform-plan
    return file_path if isinstance(file_path, str) else str(file_path.file_path)
