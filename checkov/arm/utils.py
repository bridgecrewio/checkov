from __future__ import annotations

import os
from enum import Enum
from typing import Iterable, Callable, Any

from checkov.arm.parser.parser import parse
from checkov.common.runners.base_runner import filter_ignored_paths

ARM_POSSIBLE_ENDINGS = [".json"]


class ArmElements(str, Enum):
    OUTPUTS = "outputs"
    PARAMETERS = "parameters"
    RESOURCES = "resources"
    VARIABLES = "variables"

    def __str__(self) -> str:
        # needed, because of a Python 3.11 change
        return self.value


def get_scannable_file_paths(root_folder: str | None = None, excluded_paths: list[str] | None = None) -> set[str]:
    """Finds ARM files"""

    file_paths: "set[str]" = set()
    if not root_folder:
        return file_paths

    for root, d_names, f_names in os.walk(root_folder):
        filter_ignored_paths(root, d_names, excluded_paths)
        filter_ignored_paths(root, f_names, excluded_paths)
        for file in f_names:
            file_ending = os.path.splitext(file)[1]
            if file_ending in ARM_POSSIBLE_ENDINGS:
                file_paths.add(os.path.join(root, file))

    return file_paths


def get_files_definitions(
    files: Iterable[str], filepath_fn: Callable[[str], str] | None = None
) -> tuple[dict[str, dict[str, Any]], dict[str, list[tuple[int, str]]], list[str]]:
    """Parses ARM files into its definitions and raw data"""

    definitions = {}
    definitions_raw = {}
    parsing_errors = []

    for file in files:
        result = parse(file)

        definition, definition_raw = result
        if definition is not None and definition_raw is not None:  # this has to be a 'None' check
            path = filepath_fn(file) if filepath_fn else file
            definitions[path] = definition
            definitions_raw[path] = definition_raw
        else:
            parsing_errors.append(os.path.normpath(file))

    return definitions, definitions_raw, parsing_errors
