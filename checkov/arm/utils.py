from __future__ import annotations

import logging
import os
from enum import Enum
from typing import Iterable, Callable, Any
from collections.abc import Collection
from pathlib import Path

from checkov.arm.parser.parser import parse
from checkov.common.runners.base_runner import filter_ignored_paths
from checkov.runner_filter import RunnerFilter

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


def create_definitions(
    root_folder: str,
    _: Collection[Path] | None = None,
    runner_filter: RunnerFilter | None = None,
) -> tuple[dict[str, dict[str, Any]], dict[str, list[tuple[int, str]]]]:
    definitions: dict[str, dict[str, Any]] = {}
    definitions_raw: dict[str, list[tuple[int, str]]] = {}
    parsing_errors: list[str] = []
    runner_filter = runner_filter or RunnerFilter()

    if root_folder:
        file_paths = get_scannable_file_paths(root_folder, runner_filter.excluded_paths)
        filepath_fn = lambda f: f"/{os.path.relpath(f, os.path.commonprefix((root_folder, f)))}"
        definitions, definitions_raw, parsing_errors = get_files_definitions(files=file_paths, filepath_fn=filepath_fn)

    if parsing_errors:
        logging.warning(f"[arm] found errors while parsing definitions: {parsing_errors}")

    return definitions, definitions_raw


def get_files_definitions(
        files: Iterable[str],
        filepath_fn: Callable[[str], str] | None = None,
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


def extract_resource_name_from_resource_id_func(resource_id: str) -> str:
    '''
        Examples:
            resourceId('Microsoft.Network/virtualNetworks/', virtualNetworkName) -> virtualNetworkName
    '''
    return clean_string(resource_id.split(',')[-1].split(')')[0])


def extract_resource_name_from_reference_func(reference: str) -> str:
    '''
        Examples:
                reference('storageAccountName') -> storageAccountName
                reference('myStorage').primaryEndpoints -> myStorage
                reference('myStorage', '2022-09-01', 'Full').location -> myStorage
                reference(resourceId('storageResourceGroup', 'Microsoft.Storage/storageAccounts', 'storageAccountName')), '2022-09-01') -> storageAccountName
                reference(resourceId('Microsoft.Network/publicIPAddresses', 'ipAddressName')) -> ipAddressName
    '''
    resource_name = ')'.join(reference.split('reference(', 1)[1].split(')')[:-1])
    if 'resourceId' in resource_name:
        return clean_string(
            ''.join(resource_name.split('resourceId(', 1)[1].split(')')[0]).split(',')[-1])
    else:
        return clean_string(resource_name.split(',')[0].split('/')[-1])


def clean_string(input: str) -> str:
    return input.replace("'", '').replace(" ", "")
