from __future__ import annotations

import logging
import os
from collections.abc import Iterable
from pathlib import Path
from typing import TYPE_CHECKING, Callable

from checkov.common.runners.base_runner import filter_ignored_paths
from checkov.common.util.dockerfile import is_docker_file
from checkov.dockerfile.parser import parse

if TYPE_CHECKING:
    from dockerfile_parse.parser import _Instruction  # only in extra_stubs
    from typing_extensions import Literal

DOCKERFILE_STARTLINE: Literal["startline"] = "startline"
DOCKERFILE_ENDLINE: Literal["endline"] = "endline"


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
            if is_docker_file(file):
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
