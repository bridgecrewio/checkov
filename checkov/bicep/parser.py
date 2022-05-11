from __future__ import annotations

import logging
import os
from typing import Optional
from collections.abc import Collection
from pathlib import Path

from checkov.common.runners.base_runner import filter_ignored_paths
from checkov.runner_filter import RunnerFilter
from pycep import BicepParser
from pycep.typing import BicepJson


BICEP_POSSIBLE_ENDINGS = [".bicep"]


class Parser:
    def __init__(self) -> None:
        self.bicep_parser = BicepParser(add_line_numbers=True)

    def parse(self, file_path: Path) -> tuple[BicepJson, list[tuple[int, str]]] | tuple[None, None]:
        content = file_path.read_text()

        try:
            template = self.bicep_parser.parse(text=content)
        except Exception:
            logging.error(f"[bicep] Couldn't parse {file_path}", exc_info=True)
            return None, None

        file_lines = [(idx + 1, line) for idx, line in enumerate(content.splitlines(keepends=True))]

        return template, file_lines

    def get_files_definitions(
        self, file_paths: "Collection[Path]"
    ) -> tuple[dict[Path, BicepJson], dict[Path, list[tuple[int, str]]], list[str]]:
        logging.info(f"[bicep] start to parse {len(file_paths)} files")

        definitions: dict[Path, BicepJson] = {}
        definitions_raw: dict[Path, list[tuple[int, str]]] = {}
        parsing_errors: list[str] = []

        for file_path in file_paths:
            template, file_lines = self.parse(file_path)
            if template and file_lines:
                definitions[file_path] = template
                definitions_raw[file_path] = file_lines
            else:
                parsing_errors.append(os.path.normpath(file_path.absolute()))

        logging.info(f"[bicep] successfully parsed {len(definitions)} files")

        return definitions, definitions_raw, parsing_errors

    def get_folder_definitions(
            self, root_folder: str, excluded_paths: Optional[list[str]]
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

        return self.get_files_definitions(files_list)

    def create_definitions(
            self, root_folder: str,
            files: "Collection[Path] | None" = None,
            runner_filter: RunnerFilter = RunnerFilter(),
    ) -> tuple[dict[Path, BicepJson], dict[Path, list[tuple[int, str]]]]:
        definitions: dict[Path, BicepJson] = {}
        definitions_raw: dict[Path, list[tuple[int, str]]] = {}
        parsing_errors: list[str] = []
        if files:
            definitions, definitions_raw, parsing_errors = self.get_files_definitions(file_paths=files)

        if root_folder:
            definitions, definitions_raw, parsing_errors = self.get_folder_definitions(root_folder,
                                                                                  runner_filter.excluded_paths)

        if parsing_errors:
            logging.warning(f"[bicep] found errors while parsing definitions: {parsing_errors}")

        return definitions, definitions_raw
