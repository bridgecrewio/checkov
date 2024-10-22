from __future__ import annotations

import logging
import os
from collections.abc import Iterable
from pathlib import Path
from typing import TYPE_CHECKING, Callable, Any, Literal

from dockerfile_parse.constants import COMMENT_INSTRUCTION

from checkov.common.runners.base_runner import filter_ignored_paths
from checkov.common.util.dockerfile import is_dockerfile
from checkov.common.util.suppression import collect_suppressions_for_context
from checkov.dockerfile.parser import parse

if TYPE_CHECKING:
    from dockerfile_parse.parser import _Instruction  # only in extra_stubs

DOCKERFILE_STARTLINE: Literal["startline"] = "startline"
DOCKERFILE_ENDLINE: Literal["endline"] = "endline"
DOCKERFILE_VALUE: Literal["value"] = "value"


def get_scannable_file_paths(
    root_folder: str | Path | None = None, excluded_paths: list[str] | None = None
) -> set[str]:
    """Finds Dockerfiles"""

    file_paths: "set[str]" = set()
    if not root_folder:
        return file_paths

    for root, d_names, f_names in os.walk(root_folder):
        filter_ignored_paths(root, d_names, excluded_paths)
        filter_ignored_paths(root, f_names, excluded_paths)
        for file in f_names:
            if is_dockerfile(file):
                file_path = os.path.join(root, file)
                file_paths.add(file_path)

    return file_paths


def get_files_definitions(
    files: Iterable[str], filepath_fn: Callable[[str], str] | None = None
) -> tuple[dict[str, dict[str, list[_Instruction]]], dict[str, list[str]]]:
    """Parses Dockerfiles into its definitions and raw data"""

    definitions = {}
    definitions_raw = {}

    for file in files:
        try:
            result = parse(file)

            path = filepath_fn(file) if filepath_fn else file
            definitions[path], definitions_raw[path] = result
        except TypeError:
            logging.info(f"Dockerfile skipping {file} as it is not a valid dockerfile template")
        except UnicodeDecodeError:
            logging.info(f"Dockerfile skipping {file} as it can't be read as text file")

    return definitions, definitions_raw


def get_abs_path(root_folder: str | None, file_path: str) -> str:
    """Creates the abs path

    There are a few cases here. If -f was used, there could be a leading / because it's an absolute path,
    or there will be no leading slash; root_folder will always be none.
    If -d is used, root_folder will be the value given, and -f will start with a / (hardcoded above).
    The goal here is simply to get a valid path to the file (which dockerfile_path does not always give).
    """

    if root_folder and file_path.startswith("/"):
        # remove the leading slash, if it exists
        file_path = file_path[1:]

    path_to_convert = os.path.join(root_folder, file_path) if root_folder else file_path

    return os.path.abspath(path_to_convert)


def build_definitions_context(
    definitions: dict[str, dict[str, list[_Instruction]]],
    definitions_raw: dict[str, list[str]]
) -> dict[str, dict[str, Any]]:
    definitions_context: dict[str, dict[str, Any]] = {}

    for file_path, definition in definitions.items():
        file_path = str(file_path)
        definitions_context[file_path] = {}
        skipped_checks = []
        if COMMENT_INSTRUCTION in definition:
            # collect skipped check comments
            comments = definition[COMMENT_INSTRUCTION]
            comment_lines = [(comment[DOCKERFILE_STARTLINE], comment[DOCKERFILE_VALUE]) for comment in comments]
            skipped_checks = collect_suppressions_for_context(code_lines=comment_lines)

        for instruction_name, instructions in definition.items():
            if instruction_name == COMMENT_INSTRUCTION:
                continue

            definitions_context[file_path][instruction_name] = []
            for instruction in instructions:
                start_line = instruction[DOCKERFILE_STARTLINE]
                end_line = instruction[DOCKERFILE_ENDLINE]
                code_lines = [
                    (line + 1, definitions_raw[file_path][line])
                    for line in range(start_line, end_line + 1)
                ]
                definition_resource = {
                    "start_line": start_line + 1,  # lines start with index 0
                    "end_line": end_line + 1,
                    "code_lines": code_lines,
                    "skipped_checks": skipped_checks,
                }
                definitions_context[file_path][instruction_name].append(definition_resource)

    return definitions_context
