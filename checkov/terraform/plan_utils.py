import json
import logging
import os
from typing import Dict, List, Tuple, Any, Optional
import dpath

from checkov.terraform.context_parsers.registry import parser_registry
from checkov.terraform.plan_parser import parse_tf_plan
from checkov.common.runners.base_runner import filter_ignored_paths
from checkov.runner_filter import RunnerFilter
from checkov.common.parsers.node import DictNode


def create_definitions(
    root_folder: str,
    files: Optional[List[str]] = None,
    runner_filter: RunnerFilter = RunnerFilter(),
    out_parsing_errors: Dict[str, str] = {}
) -> Tuple[Dict[str, DictNode], Dict[str, List[Tuple[int, str]]]]:
    if root_folder:
        files = [] if not files else files
        for root, d_names, f_names in os.walk(root_folder):
            filter_ignored_paths(root, d_names, runner_filter.excluded_paths)
            filter_ignored_paths(root, f_names, runner_filter.excluded_paths)
            for file in f_names:
                file_ending = os.path.splitext(file)[1]
                if file_ending == '.json':
                    try:
                        with open(f'{root}/{file}') as f:
                            content = json.load(f)
                        if isinstance(content, dict) and content.get('terraform_version'):
                            files.append(os.path.join(root, file))
                    except Exception as e:
                        logging.debug(f'Failed to load json file {root}/{file}, skipping')
                        logging.debug('Failure message:')
                        logging.debug(e, stack_info=True)
                        out_parsing_errors[file] = str(e)
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


def build_definitions_context(definitions: Dict[str, DictNode], definitions_raw: Dict[str, List[Tuple[int, str]]]) -> \
        Dict[str, Dict[str, Any]]:
    definitions_context = {}
    block_type = 'resource'
    for full_file_path, definition in definitions.items():
        entities = definition.get(block_type, [])
        for entity in entities:
            context_parser = parser_registry.context_parsers[block_type]
            definition_path = context_parser.get_entity_context_path(entity)
            entity_id = ".".join(definition_path)
            # Entity can exist only once per dir, for file as well
            entity_context = get_entity_context(definitions, definitions_raw, definition_path, full_file_path)
            dpath.new(definitions_context, [full_file_path, entity_id], entity_context)
    return definitions_context


def get_entity_context(definitions, definitions_raw, definition_path, full_file_path):
    # return self.context.get(full_file_path, {})
    entity_context = {}

    if full_file_path not in definitions:
        logging.debug(
            f'Tried to look up file {full_file_path} in TF plan entity definitions, but it does not exist')
        return entity_context

    for resource in definitions.get(full_file_path, {}).get('resource', []):
        resource_type = definition_path[0]
        if resource_type in resource.keys():
            resource_name = definition_path[1]
            if resource_name in resource[resource_type].keys():
                resource_defintion = resource[resource_type][resource_name]
                entity_context['start_line'] = resource_defintion['start_line'][0]
                entity_context['end_line'] = resource_defintion['end_line'][0]
                entity_context["code_lines"] = definitions_raw[full_file_path][
                                               entity_context["start_line"]: entity_context["end_line"]]
                entity_context['address'] = resource_defintion['__address__']
                return entity_context
    return entity_context
