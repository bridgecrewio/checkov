from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

import yaml
from jsonschema import validate, ValidationError

from checkov.common.parsers.yaml.loader import SafeLineLoaderGhaSchema
from checkov.common.parsers.yaml.parser import parse
from checkov.common.util.type_forcers import force_dict
from checkov.github_actions.schemas import gha_schema, gha_workflow

WORKFLOW_DIRECTORY = ".github/workflows/"


def get_scannable_file_paths(root_folder: str | Path) -> set[Path]:
    """Finds yaml files"""

    file_paths: set[Path] = set()

    if root_folder:
        root_path = root_folder if isinstance(root_folder, Path) else Path(root_folder)
        file_paths = {file_path for file_path in root_path.rglob("*.[y][am]*[l]") if file_path.is_file()}

    return file_paths


def parse_file(
    f: str | Path, file_content: str | None = None
) -> tuple[dict[str, Any] | list[dict[str, Any]], list[tuple[int, str]]] | None:
    file_path = f if isinstance(f, Path) else Path(f)

    if is_workflow_file(file_path):
        if not file_content:
            file_content = file_path.read_text()

        entity_schema = parse(filename=str(f), file_content=file_content)

        if entity_schema and is_schema_valid(yaml.load(file_content, Loader=SafeLineLoaderGhaSchema)):  # nosec
            return entity_schema
    return None


def is_workflow_file(file_path: str | Path) -> bool:
    """
    :return: True if the file mentioned is in a github action workflow directory and is a YAML file. Otherwise: False
    """
    abspath = os.path.abspath(file_path)
    return WORKFLOW_DIRECTORY in abspath and abspath.endswith(("yml", "yaml"))


def is_schema_valid(config: dict[str, Any] | list[dict[str, Any]]) -> bool:
    config_dict = force_dict(config)

    try:
        validate(config_dict, gha_workflow)
        return True
    except ValidationError:
        try:
            validate(config_dict, gha_schema)
            return True
        except ValidationError:
            logging.info(
                "Given entity configuration does not match the schema\n" f"config={json.dumps(config_dict, indent=4)}\n"
            )

    return False
