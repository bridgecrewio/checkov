from __future__ import annotations

import os
import logging
from collections.abc import Collection
from enum import Enum
from typing import Callable, Any, Optional
from pathlib import Path

from checkov.common.parallelizer.parallel_runner import parallel_runner
from checkov.runner_filter import RunnerFilter
from checkov.cloudformation import cfn_utils
from checkov.serverless.parsers.parser import parse
from checkov.common.runners.base_runner import filter_ignored_paths
from checkov.serverless.registry import sls_registry
from checkov.serverless.base_registry import ServerlessRegistry, EntityDetails

SLS_FILE_MASK = os.getenv(
    "CKV_SLS_FILE_MASK", "serverless.yml,serverless.yaml").split(",")


class ServerlessElements(str, Enum):
    PARAMS = "params"
    FUNCTIONS = "functions"
    PROVIDER = "provider"
    LAYERS = "layers"
    CUSTOM = "custom"
    PACKAGE = "package"
    PLUGINS = "plugins"
    SERVICE = "service"
    RESOURCES = "resources"

    def __str__(self) -> str:
        # needed, because of a Python 3.11 change
        return self.value


def create_definitions(
    root_folder: str,
    files: Collection[Path] | None = None,
    runner_filter: RunnerFilter | None = None,
) -> tuple[dict[str, dict[str, Any]], dict[str, list[tuple[int, str]]]]:
    definitions: dict[str, dict[str, Any]] = {}
    definitions_raw: dict[str, list[tuple[int, str]]] = {}
    runner_filter = runner_filter or RunnerFilter()

    if root_folder:
        file_paths = get_scannable_file_paths(root_folder, runner_filter.excluded_paths)
        definitions, definitions_raw = get_files_definitions(files=file_paths)

    return definitions, definitions_raw


def get_scannable_file_paths(root_folder: str | None = None, excluded_paths: list[str] | None = None) -> list[str]:
    files_list: list[str] = []

    if not root_folder:
        return files_list

    for root, d_names, f_names in os.walk(root_folder):
        # Don't walk in to "node_modules" directories under the root folder. If for some reason
        # scanning one of these is desired, it can be directly specified.
        if "node_modules" in d_names:
            d_names.remove("node_modules")

        filter_ignored_paths(root, d_names, excluded_paths)
        filter_ignored_paths(root, f_names, excluded_paths)
        for file in f_names:
            if file in SLS_FILE_MASK:
                files_list.append(os.path.join(root, file))

    return files_list


def get_files_definitions(
        files: list[str], filepath_fn: Callable[[str], str] | None = None
) -> tuple[dict[str, dict[str, Any]], dict[str, list[tuple[int, str]]]]:
    results = parallel_runner.run_function(_parallel_parse, files)
    definitions = {}
    definitions_raw = {}
    for file, result in results:
        if result:
            path = filepath_fn(file) if filepath_fn else file
            definitions[path], definitions_raw[path] = result

    return definitions, definitions_raw


def _parallel_parse(f: str) -> tuple[str, tuple[dict[str, Any], list[tuple[int, str]]] | None]:
    """Thin wrapper to return filename with parsed content"""
    return f, parse(f)


def get_resource_tags(entity: EntityDetails, registry: ServerlessRegistry = sls_registry) -> Optional[dict[str, str]]:
    entity_details = registry.extract_entity_details(entity)

    if not entity_details:
        return None

    entity_config = entity_details[-1]

    if not isinstance(entity_config, dict):
        return None

    try:
        tags = entity_config.get("tags")
        if tags:
            return cfn_utils.parse_entity_tags(tags)
    except Exception as e:
        logging.warning(f"Failed to parse tags for entity {entity} due to {e}")

    return None
