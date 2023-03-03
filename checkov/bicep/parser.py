from __future__ import annotations

import logging
import os
from collections.abc import Collection
from pathlib import Path
from typing import TYPE_CHECKING

from pycep import BicepParser

if TYPE_CHECKING:
    from pycep.typing import BicepJson


class Parser:
    def __init__(self) -> None:
        self.bicep_parser = BicepParser(add_line_numbers=True)

    def parse(self, file_path: Path) -> tuple[BicepJson, list[tuple[int, str]]] | tuple[None, None]:
        content = file_path.read_text()

        try:
            template = self.bicep_parser.parse(text=content)
        except Exception:
            logging.debug(f"[bicep] Couldn't parse {file_path}", exc_info=True)
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
