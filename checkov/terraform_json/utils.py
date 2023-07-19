from __future__ import annotations

import logging
import re
from collections.abc import Collection
from pathlib import Path
from typing import Any

from checkov.common.resource_code_logger_filter import add_resource_code_filter_to_logger
from checkov.terraform_json.parser import parse

TF_JSON_POSSIBLE_FILE_ENDINGS = (".tf.json",)

logger = logging.getLogger(__name__)
add_resource_code_filter_to_logger(logger)


def get_scannable_file_paths(
    root_folder: str | Path | None = None, files: list[str] | None = None, excluded_paths: list[str] | None = None
) -> set[Path]:
    """Finds Terraform JSON files"""

    file_paths: set[Path] = set()

    if root_folder:
        root_path = Path(root_folder)
        file_paths = {
            file_path
            for file_ending in TF_JSON_POSSIBLE_FILE_ENDINGS
            for file_path in root_path.rglob(f"*{file_ending}")
            if file_path.is_file()
        }

        if excluded_paths:
            compiled = [re.compile(p.replace(".terraform", r"\.terraform")) for p in excluded_paths]
            file_paths = {
                file_path for file_path in file_paths if not any(pattern.search(str(file_path)) for pattern in compiled)
            }
    if files:
        for file in files:
            if file.endswith(TF_JSON_POSSIBLE_FILE_ENDINGS):
                file_paths.add(Path(file))

    return file_paths


def create_definitions(
    file_paths: Collection[Path],
) -> tuple[dict[str, dict[str, Any]], dict[str, list[tuple[int, str]]], list[str]]:
    """Creates dict objects and code lines for given files"""

    logger.info(f"Start to parse {len(file_paths)} files")

    definitions: "dict[str, dict[str, Any]]" = {}
    definitions_raw: "dict[str, list[tuple[int, str]]]" = {}
    parsing_errors: "list[str]" = []

    for file_path in file_paths:
        template, file_lines = parse(file_path)
        if template and file_lines:
            file_path_str = str(file_path)
            definitions[file_path_str] = template
            definitions_raw[file_path_str] = file_lines
        else:
            parsing_errors.append(str(file_path.resolve()))

    logging.info(f"Successfully parsed {len(definitions)} files")

    return definitions, definitions_raw, parsing_errors
