from __future__ import annotations
from collections import defaultdict

import json
import logging
import os
from typing import Dict, List, Tuple, Any
from charset_normalizer import from_fp

from checkov.terraform.context_parsers.registry import parser_registry
from checkov.terraform.plan_parser import parse_tf_plan, TF_PLAN_RESOURCE_ADDRESS
from checkov.common.runners.base_runner import filter_ignored_paths
from checkov.runner_filter import RunnerFilter


def create_definitions(
    root_folder: str | None,
    files: list[str] | None = None,
    runner_filter: RunnerFilter | None = None,
    out_parsing_errors: dict[str, str] | None = None,
) -> tuple[dict[str, dict[str, Any]], dict[str, list[tuple[int, str]]]]:
    runner_filter = runner_filter or RunnerFilter()
    out_parsing_errors = {} if out_parsing_errors is None else out_parsing_errors

    if root_folder:
        files = [] if not files else files
        for root, d_names, f_names in os.walk(root_folder):
            filter_ignored_paths(root, d_names, runner_filter.excluded_paths)
            filter_ignored_paths(root, f_names, runner_filter.excluded_paths)
            for file in f_names:
                file_ending = os.path.splitext(file)[1]
                if file_ending == '.json':
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "rb") as f:
                            try:
                                content = json.load(f)
                            except UnicodeDecodeError:
                                logging.debug(f"Encoding for file {file_path} is not UTF-8, trying to detect it")
                                content = str(from_fp(f).best())

                        if isinstance(content, dict) and content.get('terraform_version'):
                            files.append(file_path)
                    except Exception as e:
                        logging.debug(f'Failed to load json file {file_path}, skipping', stack_info=True)
                        out_parsing_errors[file_path] = str(e)

    tf_definitions = {}
    definitions_raw = {}
    if files:
        files = [os.path.realpath(file) for file in files]
        for file in files:
            if file.endswith(".json"):
                current_tf_definitions, current_definitions_raw = parse_tf_plan(file, out_parsing_errors)
                if current_tf_definitions and current_definitions_raw:
                    tf_definitions[file] = current_tf_definitions
                    definitions_raw[file] = current_definitions_raw
            else:
                logging.debug(f'Failed to load {file} as is not a .json file, skipping')
    return tf_definitions, definitions_raw


def build_definitions_context(
    definitions: dict[str, dict[str, list[dict[str, Any]]]],
    definitions_raw: Dict[str, List[Tuple[int, str]]]
) -> Dict[str, Dict[str, Any]]:
    definitions_context: dict[str, dict[str, Any]] = defaultdict(dict)
    supported_block_types = ("data", "resource")
    for full_file_path, definition in definitions.items():
        for block_type in supported_block_types:
            entities = definition.get(block_type, [])
            for entity in entities:
                context_parser = parser_registry.context_parsers[block_type]
                definition_path = context_parser.get_entity_context_path(entity)

                if len(definition_path) > 1:
                    resource_type = definition_path[0]
                    resource_name = definition_path[1]
                    entity_id = entity.get(resource_type, {}).get(resource_name, {}).get(TF_PLAN_RESOURCE_ADDRESS)
                else:
                    entity_id = definition_path[0]

                # Entity can exist only once per dir, for file as well
                entity_context = get_entity_context(
                    definitions=definitions,
                    definitions_raw=definitions_raw,
                    definition_path=definition_path,
                    full_file_path=full_file_path,
                    entity_id=entity_id,
                    block_type=block_type,
                )
                definitions_context[full_file_path][entity_id] = entity_context
    return definitions_context


def get_entity_context(
    definitions: dict[str, dict[str, list[dict[str, Any]]]],
    definitions_raw: dict[str, list[tuple[int, str]]],
    definition_path: list[str],
    full_file_path: str,
    entity_id: str,
    block_type: str = "resource",
) -> dict[str, Any]:
    entity_context: dict[str, Any] = {}

    if full_file_path not in definitions:
        logging.debug(
            f'Tried to look up file {full_file_path} in TF plan entity definitions, but it does not exist')
        return entity_context

    for resource in definitions.get(full_file_path, {}).get(block_type, []):
        resource_type = definition_path[0]
        resource_type_dict = resource.get(resource_type)
        if not resource_type_dict:
            continue
        resource_name = definition_path[1]
        resource_defintion = resource_type_dict.get(resource_name, {})
        if resource_defintion and resource_defintion.get(TF_PLAN_RESOURCE_ADDRESS) == entity_id:
            entity_context['start_line'] = resource_defintion['start_line'][0]
            entity_context['end_line'] = resource_defintion['end_line'][0]
            entity_context["code_lines"] = definitions_raw[full_file_path][
                entity_context["start_line"] : entity_context["end_line"]
            ]
            entity_context['address'] = resource_defintion[TF_PLAN_RESOURCE_ADDRESS]
            return entity_context
    return entity_context


def get_resource_id_without_nested_modules(address: str) -> str:
    """
    return resource id with the last module in the address
    example: from address='module.name1.module.name2.type.name' return 'module: module.name2.type.name'
    """
    return ".".join(address.split(".")[-4:])
