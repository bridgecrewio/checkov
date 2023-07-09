from __future__ import annotations

import json
import logging
import os
import platform
from pathlib import Path
from typing import Any, Tuple
import dpath

import yaml
from jsonschema import validate, ValidationError

from checkov.common.parsers.yaml.loader import SafeLineLoaderGhaSchema
from checkov.common.parsers.yaml.parser import parse
from checkov.common.util.file_utils import read_file_with_any_encoding
from checkov.common.util.type_forcers import force_dict
from checkov.github_actions.graph_builder.graph_components.resource_types import ResourceType
from checkov.github_actions.schemas import gha_schema, gha_workflow
from checkov.runner_filter import RunnerFilter

WORKFLOW_DIRECTORY = ".github/workflows/"
WIN_WORKFLOW_DIRECTORY = ".github\\workflows\\"


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
            file_content = read_file_with_any_encoding(file_path=file_path)

        entity_schema = parse(filename=str(f), file_content=file_content)

        if entity_schema and is_schema_valid(yaml.load(file_content, Loader=SafeLineLoaderGhaSchema)):  # nosec
            return entity_schema
    return None


def is_workflow_file(file_path: str | Path) -> bool:
    """
    :return: True if the file mentioned is in a github action workflow directory and is a YAML file. Otherwise: False
    """
    abspath = os.path.abspath(file_path)
    return get_workflow_dir() in abspath and abspath.endswith(("yml", "yaml"))


def get_workflow_dir() -> str:
    """
    Detects os and uses different dir string
    """
    if platform.system() == "Windows":
        return WIN_WORKFLOW_DIRECTORY
    return WORKFLOW_DIRECTORY


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


def get_gha_files_definitions(root_folder: str | Path,
                              files: "list[str] | None" = None,
                              runner_filter: RunnerFilter | None = None,) -> tuple[dict[str, Any], dict[str, Any]]:
    definitions = {}
    definitions_raw = {}
    file_paths = get_scannable_file_paths(root_folder=root_folder)
    files_set = set(files) if files else set()

    for file_path in file_paths:
        str_file_path = str(file_path)
        should_parse: bool = str_file_path in files_set if files_set else True
        if should_parse:
            result = parse_file(f=file_path)
            # result should be tuple of dict representing the file payload structure and list of lines of the payload
            if result is not None:
                definitions[str_file_path] = result[0]
                definitions_raw[str_file_path] = result[1]

    return definitions, definitions_raw


def build_gha_definitions_context(definitions: dict[str, dict[str, Any]], definitions_raw: dict[str, list[Tuple[int, str]]]) -> dict[str, dict[str, Any]]:
    definitions_context: dict[str, dict[str, Any]] = {}
    resources = [e.value for e in ResourceType]
    # iterate on the files
    for file_path, file_path_definitions in definitions.items():
        # iterate on the definitions (Parameters, Resources, Outputs...)
        for file_path_definition, definition in file_path_definitions.items():
            if isinstance(file_path_definition, str) and file_path_definition in resources:
                # iterate on the actual objects of each definition
                if isinstance(definition, dict):
                    for attribute, attr_value in definition.items():
                        if isinstance(attr_value, dict):
                            start_line = attr_value['__startline__']
                            end_line = attr_value['__endline__']
                        elif isinstance(attr_value, str) and '__startline__' in definition and '__endline__' in definition:
                            start_line = definition['__startline__']
                            end_line = definition['__endline__']
                        else:
                            continue

                        code_lines = definitions_raw[file_path][start_line - 1: end_line - 1]
                        dpath.new(
                            definitions_context,
                            [file_path, str(file_path_definition), str(attribute)],
                            {"start_line": start_line, "end_line": end_line, "code_lines": code_lines},
                        )
                elif isinstance(definition, (str, list)):
                    for line_tuple in definitions_raw[file_path]:
                        if file_path_definition in line_tuple[1] and definition_locator_helper(definition, line_tuple[1]):
                            code_lines = definitions_raw[file_path][line_tuple[0] - 1:line_tuple[0]]
                            dpath.new(
                                definitions_context,
                                [file_path, str(file_path_definition), str(definition)],
                                {"start_line": line_tuple[0], "end_line": line_tuple[0] + 1, "code_lines": code_lines},
                            )
                            break

    return definitions_context


def definition_locator_helper(definition: str | list[str], target: str) -> bool:
    if isinstance(definition, str):
        return definition in target
    elif isinstance(definition, list):
        return all(item in target for item in definition)
    return False
