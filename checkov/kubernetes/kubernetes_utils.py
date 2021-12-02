import logging
import os
from copy import deepcopy
from typing import Tuple, Dict, Optional, List, Any

import dpath

from checkov.common.bridgecrew.platform_integration import bc_integration
from checkov.common.models.consts import YAML_COMMENT_MARK
from checkov.common.parallelizer.parallel_runner import parallel_runner
from checkov.common.runners.base_runner import filter_ignored_paths
from checkov.common.util.type_forcers import force_list
from checkov.kubernetes.parser.parser import parse

K8_POSSIBLE_ENDINGS = [".yaml", ".yml", ".json"]


def get_folder_definitions(
        root_folder: str, excluded_paths: Optional[List[str]]
) -> Tuple[Dict[str, List], Dict[str, List[Tuple[int, str]]]]:
    files_list = []
    filepath_fn = lambda f: f'/{os.path.relpath(f, os.path.commonprefix((root_folder, f)))}'
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
    return get_files_definitions(files_list, filepath_fn)


def get_files_definitions(files: List[str], filepath_fn=None) \
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
            (file, parse_result) = result
            if parse_result:
                path = filepath_fn(file) if filepath_fn else file
                (definitions[path], definitions_raw[path]) = parse_result
    return definitions, definitions_raw


def get_skipped_checks(entity_conf):
    skipped = []
    metadata = {}
    bc_id_mapping = bc_integration.get_id_mapping()
    ckv_to_bc_id_mapping = bc_integration.get_ckv_to_bc_id_mapping()
    if not isinstance(entity_conf, dict):
        return skipped
    if entity_conf["kind"] == "containers" or entity_conf["kind"] == "initContainers":
        metadata = entity_conf["parent_metadata"]
    else:
        if "metadata" in entity_conf.keys():
            metadata = entity_conf["metadata"]
    if "annotations" in metadata.keys() and metadata["annotations"] is not None:
        if isinstance(metadata["annotations"], dict):
            metadata["annotations"] = force_list(metadata["annotations"])
        for annotation in metadata["annotations"]:
            if not isinstance(annotation, dict):
                logging.debug( f"Parse of Annotation Failed for {annotation}: {entity_conf}")
                continue
            for key in annotation:
                skipped_item = {}
                if "checkov.io/skip" in key or "bridgecrew.io/skip" in key:
                    if "CKV_K8S" in annotation[key] or "BC_K8S" in annotation[key]:
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
                        logging.debug("Parse of Annotation Failed for {}: {}".format(metadata["annotations"][key], entity_conf, indent=2))
                        continue
    return skipped


def build_definitions_context(definitions: Dict[str, List], definitions_raw: Dict[str, List[Tuple[int, str]]]) -> \
        Dict[str, Dict[str, Any]]:
    definitions_context: Dict[str, Dict[str, Any]] = {}
    definitions = deepcopy(definitions)
    # iterate on the files
    for file_path, resources in definitions.items():

        for resource in resources:
            if resource.get("kind") == "List":
                resources.extend(resource.get("items", []))
                resources.remove(resource)
        # Append containers and initContainers to definitions list
        for resource in resources:
            definitions[file_path].extend(get_containers_definitions(resource))

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


def get_containers_definitions(entity_conf):
    results = []
    if is_invalid_k8_definition(entity_conf):
        return results
    metadata = entity_conf.get("metadata", {})
    # Skip entity without metadata["name"]
    # Skip entity with parent (metadata["ownerReferences"]) in runtime
    # We will alert in runtime only
    if not metadata or isinstance(metadata, int) or "name" not in metadata or \
            metadata.get("ownerReferences"):
        return results
    for type in ["containers", "initContainers"]:
        if entity_conf["kind"] == "CustomResourceDefinition":
            continue
        containers = search_deep_keys(type, entity_conf, [])
        if not containers:
            continue
        containers = containers.pop()
        namespace = metadata.get("namespace", "default")
        container_def = containers.pop()
        if not container_def:
            continue

        container_def = force_list(container_def)
        for i, cd in enumerate(container_def):
            cd["apiVersion"] = entity_conf["apiVersion"]
            cd["kind"] = type
            cd["parent"] = f'{entity_conf["kind"]}.{namespace}.{metadata.get("name")} (container {i})'
            cd["parent_metadata"] = entity_conf["metadata"]
            results.append(cd)
    return results


def search_deep_keys(searchText, obj, path):
    """Search deep for keys and get their values"""
    keys = []
    if isinstance(obj, dict):
        for key in obj:
            pathprop = path[:]
            pathprop.append(key)
            if key == searchText:
                pathprop.append(obj[key])
                keys.append(pathprop)
                # pop the last element off for nesting of found elements for
                # dict and list checks
                pathprop = pathprop[:-1]
            if isinstance(obj[key], dict):
                if key != 'parent_metadata':
                    # Don't go back to the parent metadata, it is scanned for the parent
                    keys.extend(search_deep_keys(searchText, obj[key], pathprop))
            elif isinstance(obj[key], list):
                for index, item in enumerate(obj[key]):
                    pathproparr = pathprop[:]
                    pathproparr.append(index)
                    keys.extend(search_deep_keys(searchText, item, pathproparr))
    elif isinstance(obj, list):
        for index, item in enumerate(obj):
            pathprop = path[:]
            pathprop.append(index)
            keys.extend(search_deep_keys(searchText, item, pathprop))

    return keys


def is_invalid_k8_definition(definition: dict) -> bool:
    return not isinstance(definition, dict) or 'apiVersion' not in definition.keys() or 'kind' not in \
           definition.keys() or isinstance(definition.get("kind"), int)


def get_resource_id(resource):
    resource_type = resource["kind"]
    if resource_type in ["containers", "initContainers"]:
        return resource.get("parent")
    metadata = resource.get("metadata", {})
    namespace = metadata.get("namespace", "default")
    name = metadata.get("name")
    if not name:
        return None
    return f'{resource_type}.{namespace}.{name}'
