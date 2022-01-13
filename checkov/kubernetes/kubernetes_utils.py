import logging
import os
from copy import deepcopy
from typing import Tuple, Dict, Optional, List, Any

import dpath
from checkov.runner_filter import RunnerFilter

from checkov.common.bridgecrew.platform_integration import bc_integration
from checkov.common.models.consts import YAML_COMMENT_MARK
from checkov.common.parallelizer.parallel_runner import parallel_runner
from checkov.common.parsers.node import DictNode
from checkov.common.runners.base_runner import filter_ignored_paths
from checkov.common.util.type_forcers import force_list
from checkov.kubernetes.parser.parser import parse

K8_POSSIBLE_ENDINGS = [".yaml", ".yml", ".json"]


def get_folder_definitions(
        root_folder: str, excluded_paths: Optional[List[str]]
) -> Tuple[Dict[str, List], Dict[str, List[Tuple[int, str]]]]:
    files_list = []
    for root, d_names, f_names in os.walk(root_folder):
        filter_ignored_paths(root, d_names, excluded_paths)
        filter_ignored_paths(root, f_names, excluded_paths)

        for file in f_names:
            file_ending = os.path.splitext(file)[1]
            if file_ending in K8_POSSIBLE_ENDINGS:
                full_path = os.path.join(root, file)
                if "/." not in full_path and file not in ['package.json', 'package-lock.json']:
                    # skip temp directories
                    files_list.append(full_path)
    return get_files_definitions(files_list)


def get_files_definitions(files: List[str]) \
        -> Tuple[Dict[str, List], Dict[str, List[Tuple[int, str]]]]:
    def _parse_file(filename):
        try:
            return filename, parse(filename)
        except (TypeError, ValueError) as e:
            logging.warning(f"Kubernetes skipping {filename} as it is not a valid Kubernetes template\n{e}")

    definitions = {}
    definitions_raw = {}
    results = parallel_runner.run_function(_parse_file, files)
    for result in results:
        if result:
            (path, parse_result) = result
            if parse_result:
                (definitions[path], definitions_raw[path]) = parse_result
    return definitions, definitions_raw


def get_skipped_checks(entity_conf):
    skipped = []
    metadata = {}
    bc_id_mapping = bc_integration.get_id_mapping()
    ckv_to_bc_id_mapping = bc_integration.get_ckv_to_bc_id_mapping()
    if not isinstance(entity_conf, dict):
        return skipped
    if "metadata" in entity_conf.keys():
        metadata = entity_conf["metadata"]
    if "annotations" in metadata.keys() and metadata["annotations"] is not None:
        if isinstance(metadata["annotations"], dict):
            metadata["annotations"] = force_list(metadata["annotations"])
        for annotation in metadata["annotations"]:
            if not isinstance(annotation, dict):
                logging.debug(f"Parse of Annotation Failed for {annotation}: {entity_conf}")
                continue
            for key in annotation:
                skipped_item = {}
                if "checkov.io/skip" in key or "bridgecrew.io/skip" in key:
                    if "CKV_K8S" in annotation[key] or "BC_K8S" in annotation[key] or "CKV2_K8S" in annotation[key]:
                        if "=" in annotation[key]:
                            (skipped_item["id"], skipped_item["suppress_comment"]) = annotation[key].split("=")
                        else:
                            skipped_item["id"] = annotation[key]
                            skipped_item["suppress_comment"] = "No comment provided"

                        # No matter which ID was used to skip, save the pair of IDs in the appropriate fields
                        if bc_id_mapping and skipped_item["id"] in bc_id_mapping:
                            skipped_item["bc_id"] = skipped_item["id"]
                            skipped_item["id"] = bc_id_mapping[skipped_item["id"]]
                        elif ckv_to_bc_id_mapping:
                            skipped_item["bc_id"] = ckv_to_bc_id_mapping.get(skipped_item["id"])
                        skipped.append(skipped_item)
                    else:
                        logging.debug(f"Parse of Annotation Failed for {metadata['annotations'][key]}: {entity_conf}")
                        continue
    return skipped


def create_definitions(
    root_folder: str,
    files: Optional[List[str]] = None,
    runner_filter: RunnerFilter = RunnerFilter(),
) -> Tuple[Dict[str, DictNode], Dict[str, List[Tuple[int, str]]]]:
    definitions = {}
    definitions_raw = {}
    if files:
        definitions, definitions_raw = get_files_definitions(files)

    if root_folder:
        definitions, definitions_raw = get_folder_definitions(root_folder, runner_filter.excluded_paths)

    return definitions, definitions_raw


def build_definitions_context(definitions: Dict[str, DictNode], definitions_raw: Dict[str, List[Tuple[int, str]]]) -> \
        Dict[str, Dict[str, Any]]:
    definitions_context: Dict[str, Dict[str, Any]] = {}
    definitions = deepcopy(definitions)
    # iterate on the files
    for file_path, resources in definitions.items():

        for resource in resources:
            if resource.get("kind") == "List":
                resources.extend(resource.get("items", []))
                resources.remove(resource)

        # iterate on the resources
        for resource in resources:
            if is_invalid_k8_definition(resource):
                continue
            resource_id = get_resource_id(resource)
            if not resource_id:
                continue
            start_line = resource["__startline__"]
            end_line = min(resource["__endline__"], len(definitions_raw[file_path]))
            first_line_index = 0
            # skip empty lines
            while not str.strip(definitions_raw[file_path][first_line_index][1]):
                first_line_index += 1
            # check if the file is a json file
            if str.strip(definitions_raw[file_path][first_line_index][1])[0] == "{":
                start_line += 1
                end_line += 1
            else:
                # add resource comments to definition lines
                current_line = str.strip(definitions_raw[file_path][start_line - 1][1])
                while not current_line or current_line[0] == YAML_COMMENT_MARK:
                    start_line -= 1
                    current_line = str.strip(definitions_raw[file_path][start_line - 1][1])

                # remove next resource comments from definition lines
                current_line = str.strip(definitions_raw[file_path][end_line - 1][1])
                while not current_line or current_line[0] == YAML_COMMENT_MARK:
                    end_line -= 1
                    current_line = str.strip(definitions_raw[file_path][end_line - 1][1])

            code_lines = definitions_raw[file_path][start_line - 1: end_line]
            dpath.new(
                definitions_context,
                [file_path, resource_id],
                {"start_line": start_line, "end_line": end_line, "code_lines": code_lines},
            )

            skipped_checks = get_skipped_checks(resource)
            dpath.new(
                definitions_context,
                [file_path, resource_id, "skipped_checks"],
                skipped_checks,
            )
    return definitions_context


def is_invalid_k8_definition(definition: Dict[str, Any]) -> bool:
    return (
        not isinstance(definition, dict)
        or 'apiVersion' not in definition.keys()
        or 'kind' not in definition.keys()
        or isinstance(definition.get("kind"), int)
        or not isinstance(definition.get('metadata'), dict)
    )


def get_resource_id(resource: Dict[str, Any]) -> Optional[str]:
    resource_type = resource["kind"]
    metadata = resource.get("metadata") or {}
    namespace = metadata.get("namespace", "default")
    name = metadata.get("name")
    if not name:
        return None
    return f'{resource_type}.{namespace}.{name}'
