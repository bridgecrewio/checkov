from __future__ import annotations

import os
from pathlib import Path
from typing import Optional
import logging
from collections.abc import Collection

from checkov.common.runners.base_runner import filter_ignored_paths
from checkov.runner_filter import RunnerFilter
from checkov.bicep.parser import Parser
from pycep.typing import BicepJson


BICEP_POSSIBLE_ENDINGS = [".bicep"]


def get_scannable_file_paths(root_folder: str | Path | None = None, files: list[str] | None = None) -> set[Path]:
    """Finds Bicep files"""

    file_paths: set[Path] = set()

    if root_folder:
        root_path = Path(root_folder)
        file_paths = {file_path for file_path in root_path.rglob("*.bicep")}
    if files:
        for file in files:
            if file.endswith(".bicep"):
                file_paths.add(Path(file))

    return file_paths


def clean_file_path(file_path: Path) -> Path:
    path_parts = [part for part in file_path.parts if part not in (".", "..")]

    return Path(*path_parts)


def get_folder_definitions(
    root_folder: str, excluded_paths: Optional[list[str]]
) -> tuple[dict[Path, BicepJson], dict[Path, list[tuple[int, str]]], list[str]]:
    files_list: set[Path] = set()
    for root, d_names, f_names in os.walk(root_folder):
        filter_ignored_paths(root, d_names, excluded_paths)
        filter_ignored_paths(root, f_names, excluded_paths)
        for file in f_names:
            file_ending = os.path.splitext(file)[1]
            if file_ending in BICEP_POSSIBLE_ENDINGS:
                full_path = os.path.join(root, file)
                files_list.add(Path(full_path))
    parser = Parser()

    return parser.get_files_definitions(files_list)


def create_definitions(
        root_folder: str,
        files: "Collection[Path] | None" = None,
        runner_filter: RunnerFilter = RunnerFilter(),
) -> tuple[dict[Path, BicepJson], dict[Path, list[tuple[int, str]]]]:
    definitions: dict[Path, BicepJson] = {}
    definitions_raw: dict[Path, list[tuple[int, str]]] = {}
    parsing_errors: list[str] = []
    if files:
        parser = Parser()
        definitions, definitions_raw, parsing_errors = parser.get_files_definitions(file_paths=files)

    if root_folder:
        definitions, definitions_raw, parsing_errors = get_folder_definitions(root_folder,
                                                                              runner_filter.excluded_paths)

    if parsing_errors:
        logging.warning(f"[bicep] found errors while parsing definitions: {parsing_errors}")

    return definitions, definitions_raw
