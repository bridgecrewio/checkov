from __future__ import annotations

import json
import logging
import os
from collections.abc import Sequence
from pathlib import Path
from typing import Any, Optional

import hcl2
import re

from typing_extensions import TypeAlias


ENTITY_NAME_PATTERN = re.compile(r"[^\W0-9][\w-]*")
RESOLVED_MODULE_PATTERN = re.compile(r"\[.+\#.+\]")
_Hcl2Payload: TypeAlias = "dict[str, list[dict[str, Any]]]"


def _is_valid_block(block: Any) -> bool:
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
        block_type: [block for block in blocks if _is_valid_block(block)]
        for block_type, blocks in raw_data.items()
    }


def _load_or_die_quietly(
    file: str | Path, parsing_errors: dict[str, Exception], clean_definitions: bool = True
) -> Optional[_Hcl2Payload]:
    """
Load JSON or HCL, depending on filename.
    :return: None if the file can't be loaded
    """

    file_path = os.fspath(file)
    file_name = os.path.basename(file_path)

    try:
        logging.debug(f"Parsing {file_path}")

        with open(file_path, "r", encoding="utf-8-sig") as f:
            if file_name.endswith(".json"):
                return json.load(f)
            else:
                raw_data = hcl2.load(f)
                non_malformed_definitions = validate_malformed_definitions(raw_data)
                if clean_definitions:
                    return clean_bad_definitions(non_malformed_definitions)
                else:
                    return non_malformed_definitions
    except Exception as e:
        logging.debug(f'failed while parsing file {file_path}', exc_info=True)
        parsing_errors[file_path] = e
        return None


def clean_bad_definitions(tf_definition_list: _Hcl2Payload) -> _Hcl2Payload:
    return {
        block_type: [
            definition
            for definition in definition_list
            if block_type in {"locals", "terraform"} or not isinstance(definition, dict) or len(definition) == 1
        ]
        for block_type, definition_list in tf_definition_list.items()
    }


def _safe_index(sequence_hopefully: Sequence[Any], index: int) -> Any:
    try:
        return sequence_hopefully[index]
    except IndexError:
        logging.debug(f'Failed to parse index int ({index}) out of {sequence_hopefully}', exc_info=True)
        return None


def _remove_module_dependency_in_path(path: str) -> str:
    """
    :param path: path that looks like "dir/main.tf[other_dir/x.tf#0]
    :return: only the outer path: dir/main.tf
    """
    if re.findall(RESOLVED_MODULE_PATTERN, path):
        path = re.sub(RESOLVED_MODULE_PATTERN, '', path)
    return path
