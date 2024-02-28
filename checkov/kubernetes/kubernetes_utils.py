from __future__ import annotations

import logging
import os
from typing import Dict, Any, TYPE_CHECKING

import dpath

from checkov.common.models.enums import CheckResult
from checkov.common.util.consts import LINE_FIELD_NAMES, START_LINE, END_LINE
from checkov.runner_filter import RunnerFilter
from checkov.common.bridgecrew.integration_features.features.policy_metadata_integration import integration as metadata_integration
from checkov.common.models.consts import YAML_COMMENT_MARK
from checkov.common.parallelizer.parallel_runner import parallel_runner
from checkov.common.runners.base_runner import filter_ignored_paths
from checkov.common.util.type_forcers import force_list
from checkov.kubernetes.parser.parser import parse

if TYPE_CHECKING:
    from checkov.common.typing import _SkippedCheck, _CheckResult, _EntityContext

EXCLUDED_FILE_NAMES = {"package.json", "package-lock.json"}
K8_POSSIBLE_ENDINGS = {".yaml", ".yml", ".json"}
DEFAULT_NESTED_RESOURCE_TYPE = "Pod"
SUPPORTED_POD_CONTAINERS_TYPES = {"Deployment", "DeploymentConfig", "DaemonSet", "Job", "ReplicaSet", "ReplicationController", "StatefulSet"}
PARENT_RESOURCE_KEY_NAME = "_parent_resource"
PARENT_RESOURCE_ID_KEY_NAME = "_parent_resource_id"
FILTERED_RESOURCES_FOR_EDGE_BUILDERS = ["NetworkPolicy"]


def get_folder_definitions(
        root_folder: str, excluded_paths: list[str] | None
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, list[tuple[int, str]]]]:
    files_list = []
    for root, d_names, f_names in os.walk(root_folder):
        filter_ignored_paths(root, d_names, excluded_paths)
        filter_ignored_paths(root, f_names, excluded_paths)

        for file in f_names:
            file_ending = os.path.splitext(file)[1]
            if file_ending in K8_POSSIBLE_ENDINGS:
                full_path = os.path.join(root, file)
                if "/." not in full_path and file not in EXCLUDED_FILE_NAMES:
                    # skip temp directories
                    files_list.append(full_path)
    return get_files_definitions(files_list)


def get_files_definitions(files: list[str]) -> tuple[dict[str, list[dict[str, Any]]], dict[str, list[tuple[int, str]]]]:
    definitions = {}
    definitions_raw = {}
    results = parallel_runner.run_function(_parse_file, files)
    for result in results:
        if result:
            path, parse_result = result
            if parse_result:
                definitions[path], definitions_raw[path] = parse_result
    return definitions, definitions_raw


def _parse_file(filename: str) -> tuple[str, tuple[list[dict[str, Any]], list[tuple[int, str]]] | None] | None:
    try:
        return filename, parse(filename)
    except (TypeError, ValueError):
        logging.warning(f"Kubernetes skipping {filename} as it is not a valid Kubernetes template", exc_info=True)

    return None


def get_skipped_checks(entity_conf: dict[str, Any]) -> list[_SkippedCheck]:
    skipped = []
    metadata = {}
    bc_id_mapping = metadata_integration.bc_to_ckv_id_mapping
    if not isinstance(entity_conf, dict):
        return skipped
    if "metadata" in entity_conf.keys():
        metadata = entity_conf["metadata"]
    if metadata and "annotations" in metadata.keys() and metadata["annotations"] is not None:
        if isinstance(metadata["annotations"], dict):
            metadata["annotations"] = force_list(metadata["annotations"])
        for annotation in metadata["annotations"]:
            if not isinstance(annotation, dict):
                logging.debug(f"Parse of Annotation Failed for {annotation}: {entity_conf}")
                continue
            for key in annotation:
                skipped_item: "_SkippedCheck" = {}
                if "checkov.io/skip" in key or "bridgecrew.io/skip" in key:
                    if "=" in annotation[key]:
                        (skipped_item["id"], skipped_item["suppress_comment"]) = annotation[key].split("=")
                    else:
                        skipped_item["id"] = annotation[key]
                        skipped_item["suppress_comment"] = "No comment provided"

                    # No matter which ID was used to skip, save the pair of IDs in the appropriate fields
                    if bc_id_mapping and skipped_item["id"] in bc_id_mapping:
                        skipped_item["bc_id"] = skipped_item["id"]
                        skipped_item["id"] = bc_id_mapping[skipped_item["id"]]
                    elif metadata_integration.check_metadata:
                        skipped_item["bc_id"] = metadata_integration.get_bc_id(skipped_item["id"])
                    skipped.append(skipped_item)
    return skipped


def create_definitions(
    root_folder: str | None,
    files: list[str] | None = None,
    runner_filter: RunnerFilter | None = None,
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, list[tuple[int, str]]]]:
    runner_filter = runner_filter or RunnerFilter()
    definitions: dict[str, list[dict[str, Any]]] = {}
    definitions_raw: dict[str, list[tuple[int, str]]] = {}
    if files:
        definitions, definitions_raw = get_files_definitions(files)

    if root_folder:
        definitions, definitions_raw = get_folder_definitions(root_folder, runner_filter.excluded_paths)

    return definitions, definitions_raw


def build_definitions_context(
    definitions: dict[str, list[dict[str, Any]]], definitions_raw: dict[str, list[tuple[int, str]]]
) -> dict[str, dict[str, Any]]:
    definitions_context: Dict[str, Dict[str, Any]] = {}
    # iterate on the files
    for file_path, resources in definitions.items():
        for resource in resources[:]:
            if resource.get("kind") == "List":
                # this could be inefficient, if more than one 'List' object exists in the same file
                resources = resources[:]
                resources.extend(item for item in resource.get("items", []) if item)
                resources.remove(resource)

        # iterate on the resources
        for resource in resources:
            if is_invalid_k8_definition(resource):
                continue
            resource_id = get_resource_id(resource)
            if not resource_id:
                continue

            relative_resource_path = None
            if 'metadata' in resource:
                metadata = resource['metadata']
                if 'annotations' in metadata and metadata['annotations'] is not None\
                        and 'config.kubernetes.io/origin' in metadata['annotations']:
                    metadata_path = metadata['annotations']['config.kubernetes.io/origin']
                    if 'path:' in metadata_path:
                        relative_resource_path = metadata_path.split('path:')[1].strip()

            resource_start_line = resource[START_LINE]
            resource_end_line = min(resource[END_LINE], len(definitions_raw[file_path]))
            raw_code = definitions_raw[file_path]
            code_lines, start_line, end_line = calculate_code_lines(raw_code, resource_start_line, resource_end_line)
            dpath.new(
                definitions_context,
                [file_path, resource_id],
                {"start_line": start_line, "end_line": end_line, "code_lines": code_lines,
                 "origin_relative_path": relative_resource_path},
            )

            skipped_checks = get_skipped_checks(resource)
            dpath.new(
                definitions_context,
                [file_path, resource_id, "skipped_checks"],
                skipped_checks,
            )
    return definitions_context


def calculate_code_lines(raw_code: list[tuple[int, str]], start_line: int, end_line: int) \
        -> tuple[list[tuple[int, str]], int, int]:
    first_line_index = 0
    # skip empty lines
    while not str.strip(raw_code[first_line_index][1]):
        first_line_index += 1
    # check if the file is a json file
    if str.strip(raw_code[first_line_index][1])[0] == "{":
        start_line += 1
        end_line += 1
    else:
        # add resource comments to definition lines
        current_line = str.strip(raw_code[start_line - 1][1])
        while not current_line or current_line[0] == YAML_COMMENT_MARK:
            start_line -= 1
            current_line = str.strip(raw_code[start_line - 1][1])

        # remove next resource comments from definition lines
        current_line = str.strip(raw_code[end_line - 1][1])
        while not current_line or current_line[0] == YAML_COMMENT_MARK:
            end_line -= 1
            current_line = str.strip(raw_code[end_line - 1][1])
    code_lines = raw_code[start_line - 1: end_line]
    return code_lines, start_line, end_line


def is_invalid_k8_definition(definition: Dict[str, Any]) -> bool:
    return (
        not isinstance(definition, dict)
        or 'apiVersion' not in definition.keys()
        or 'kind' not in definition.keys()
        or isinstance(definition.get("kind"), int)
        or not isinstance(definition.get('metadata'), dict)
    )


def is_invalid_k8_pod_definition(definition: Dict[str, Any]) -> bool:
    if not isinstance(definition, dict):
        return True
    metadata = definition.get('metadata')
    if not isinstance(metadata, dict):
        return True
    spec = definition.get('spec')
    if not isinstance(spec, dict) and not isinstance(spec, list):
        return True
    labels = metadata.get('labels')
    name = metadata.get('name')
    if name is None and labels is None:
        return True
    return False


def get_resource_id(resource: dict[str, Any] | None) -> str | None:
    if not resource:
        return None

    resource_type = resource.get("kind", DEFAULT_NESTED_RESOURCE_TYPE)
    metadata = resource.get("metadata") or {}
    namespace = metadata.get("namespace", "default")
    name = metadata.get("name")
    if name:
        return f'{resource_type}.{namespace}.{name}'
    labels = metadata.get("labels")
    if labels:
        return build_resource_id_from_labels(resource_type, namespace, labels, resource)
    return None


def build_resource_id_from_labels(resource_type: str,
                                  namespace: str,
                                  labels: dict[str, str],
                                  resource: dict[str, Any]) -> str:
    labels_list = [
        f"{label}-{value}"
        for label, value in labels.items()
        if label not in LINE_FIELD_NAMES
    ]
    labels_string = ".".join(labels_list) if labels_list else "default"
    parent_resource = resource.get(PARENT_RESOURCE_KEY_NAME)
    if parent_resource:
        resource_id = f'{resource_type}.{namespace}.{parent_resource}.{labels_string}'
    else:
        resource_id = f'{resource_type}.{namespace}.{labels_string}'
    return resource_id


def remove_metadata_from_attribute(attribute: dict[str, Any] | None) -> None:
    if isinstance(attribute, dict):
        attribute.pop("__startline__", None)
        attribute.pop("__endline__", None)


def create_check_result(check_result: _CheckResult, entity_context: _EntityContext, check_id: str) -> _CheckResult:
    """Creates a cleaned version of check_result for further usage"""

    clean_check_result: _CheckResult = {
        "result": check_result["result"],
        "evaluated_keys": check_result["evaluated_keys"],
    }

    for skipped_check in entity_context.get("skipped_checks", []):
        if skipped_check["id"] == check_id:
            clean_check_result["result"] = CheckResult.SKIPPED
            clean_check_result["suppress_comment"] = skipped_check["suppress_comment"]
            break

    return clean_check_result
