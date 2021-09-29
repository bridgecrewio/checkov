import logging
import operator
import os
from functools import reduce

from checkov.common.bridgecrew.platform_integration import bc_integration
from checkov.common.util.data_structures_utils import search_deep_keys
from checkov.common.util.type_forcers import force_list
from checkov.common.output.record import Record
from checkov.common.output.report import Report
from checkov.common.runners.base_runner import BaseRunner, filter_ignored_paths
from checkov.kubernetes.parser.parser import parse
from checkov.kubernetes.registry import registry
from checkov.runner_filter import RunnerFilter

K8_POSSIBLE_ENDINGS = [".yaml", ".yml", ".json"]


class Runner(BaseRunner):
    check_type = "kubernetes"

    def run(self, root_folder, external_checks_dir=None, files=None, runner_filter=RunnerFilter(), collect_skip_comments=True, helmChart=None):
        report = Report(self.check_type)
        definitions = {}
        definitions_raw = {}
        parsing_errors = {}
        files_list = []
        if external_checks_dir:
            for directory in external_checks_dir:
                registry.load_external_checks(directory)

        if files:
            for file in files:
                parse_result = parse(file)
                if parse_result:
                    (definitions[file], definitions_raw[file]) = parse_result

        if root_folder:
            for root, d_names, f_names in os.walk(root_folder):
                filter_ignored_paths(root, d_names, runner_filter.excluded_paths)
                filter_ignored_paths(root, f_names, runner_filter.excluded_paths)

                for file in f_names:
                    file_ending = os.path.splitext(file)[1]
                    if file_ending in K8_POSSIBLE_ENDINGS:
                        full_path = os.path.join(root, file)
                        if "/." not in full_path and file not in ['package.json','package-lock.json']:
                            # skip temp directories
                            files_list.append(full_path)

            for file in files_list:
                relative_file_path = f'/{os.path.relpath(file, os.path.commonprefix((root_folder, file)))}'
                try:
                    parse_result = parse(file)
                    if parse_result:
                        (definitions[relative_file_path], definitions_raw[relative_file_path]) = parse_result
                except (TypeError, ValueError) as e:
                    logging.warning(f"Kubernetes skipping {file} as it is not a valid Kubernetes template\n{e}")
                    continue

        for k8_file in definitions.keys():

            # There are a few cases here. If -f was used, there could be a leading / because it's an absolute path,
            # or there will be no leading slash; root_folder will always be none.
            # If -d is used, root_folder will be the value given, and -f will start with a / (hardcoded above).
            # The goal here is simply to get a valid path to the file (which sls_file does not always give).
            if k8_file[0] == '/':
                path_to_convert = (root_folder + k8_file) if root_folder else k8_file
            else:
                path_to_convert = (os.path.join(root_folder, k8_file)) if root_folder else k8_file

            file_abs_path = os.path.abspath(path_to_convert)

            if definitions[k8_file]:
                for i in range(len(definitions[k8_file])):
                    if (not 'apiVersion' in definitions[k8_file][i].keys()) and (not 'kind' in definitions[k8_file][i].keys()):
                        continue
                    logging.debug("Template Dump for {}: {}".format(k8_file, definitions[k8_file][i], indent=2))

                    entity_conf = definitions[k8_file][i]
                    if entity_conf is None:
                        continue

                    # Split out resources if entity kind is List
                    if isinstance(entity_conf, dict) and entity_conf["kind"] == "List":
                        for item in entity_conf.get("items", []):
                            definitions[k8_file].append(item)

                for i in range(len(definitions[k8_file])):
                    if _is_invalid_k8_definition(definitions[k8_file][i]):
                        continue
                    logging.debug("Template Dump for {}: {}".format(k8_file, definitions[k8_file][i], indent=2))

                    entity_conf = definitions[k8_file][i]

                    if isinstance(entity_conf, dict) and entity_conf.get("kind") == "List":
                        continue

                    # Skip entity without metadata["name"]
                    if isinstance(entity_conf, dict) and entity_conf.get("metadata"):
                        if isinstance(entity_conf["metadata"], int) or "name" not in entity_conf["metadata"]:
                            continue
                    else:
                        continue

                    # Skip entity with parent (metadata["ownerReferences"]) in runtime
                    # We will alert in runtime only
                    if "ownerReferences" in entity_conf["metadata"] and \
                            entity_conf["metadata"]["ownerReferences"] is not None:
                        continue

                    # Append containers and initContainers to definitions list
                    for type in ["containers", "initContainers"]:
                        containers = []
                        if entity_conf["kind"] == "CustomResourceDefinition":
                            continue
                        containers = search_deep_keys(type, entity_conf, [])
                        if not containers:
                            continue
                        containers = containers.pop()
                        #containers.insert(0,entity_conf['kind'])
                        containerDef = {}
                        namespace = ""
                        if "namespace" in entity_conf["metadata"]:
                            namespace = entity_conf["metadata"]["namespace"]
                        else:
                            namespace = "default"
                        containerDef["containers"] = containers.pop()
                        if containerDef["containers"] is not None:
                            for cd in containerDef["containers"]:
                                i = containerDef["containers"].index(cd)
                                containerDef["containers"][i]["apiVersion"] = entity_conf["apiVersion"]
                                containerDef["containers"][i]["kind"] = type
                                containerDef["containers"][i]["parent"] = "{}.{}.{} (container {})".format(
                                    entity_conf["kind"], entity_conf["metadata"]["name"], namespace, str(i))
                                containerDef["containers"][i]["parent_metadata"] = entity_conf["metadata"]
                            definitions[k8_file].extend(containerDef["containers"])

                # Run for each definition included added container definitions
                for i in range(len(definitions[k8_file])):
                    if _is_invalid_k8_definition(definitions[k8_file][i]):
                        continue
                    logging.debug("Template Dump for {}: {}".format(k8_file, definitions[k8_file][i], indent=2))

                    entity_conf = definitions[k8_file][i]
                    if entity_conf is None:
                        continue
                    if isinstance(entity_conf, dict) and (entity_conf["kind"] == "List" or not entity_conf.get("kind")):
                        continue

                    if isinstance(entity_conf, dict) and isinstance(entity_conf.get("kind"), int):
                        continue
                    # Skip entity without metadata["name"] or parent_metadata["name"]
                    if not any(x in entity_conf["kind"] for x in ["containers", "initContainers"]):
                        if entity_conf.get("metadata"):
                            if isinstance(entity_conf["metadata"], int) or not "name" in entity_conf["metadata"]:
                                continue
                        else:
                            continue

                    # Skip entity with parent (metadata["ownerReferences"]) in runtime
                    # We will alert in runtime only
                    if "metadata" in entity_conf:
                        if "ownerReferences" in entity_conf["metadata"] and \
                                entity_conf["metadata"]["ownerReferences"] is not None:
                            continue

                    # Skip Kustomization Templates (for now)
                    if entity_conf["kind"] == "Kustomization":
                        continue

                    skipped_checks = get_skipped_checks(entity_conf)

                    results = registry.scan(k8_file, entity_conf, skipped_checks, runner_filter)

                    start_line = entity_conf["__startline__"]
                    end_line = entity_conf["__endline__"]

                    if start_line == end_line:
                        entity_lines_range = [start_line, end_line]
                        entity_code_lines = definitions_raw[k8_file][start_line - 1: end_line]
                    else:
                        entity_lines_range = [start_line, end_line - 1]
                        entity_code_lines = definitions_raw[k8_file][start_line - 1: end_line - 1]

                    # TODO? - Variable Eval Message!
                    variable_evaluations = {}

                    for check, check_result in results.items():
                        resource_id = check.get_resource_id(entity_conf)
                        report.add_resource(f'{k8_file}:{resource_id}')
                        record = Record(check_id=check.id, bc_check_id=check.bc_id, check_name=check.name, check_result=check_result,
                                        code_block=entity_code_lines, file_path=k8_file,
                                        file_line_range=entity_lines_range,
                                        resource=resource_id, evaluations=variable_evaluations,
                                        check_class=check.__class__.__module__, file_abs_path=file_abs_path)
                        report.add_record(record=record)

        return report



def get_skipped_checks(entity_conf):
    skipped = []
    metadata = {}
    bc_id_mapping = bc_integration.get_id_mapping()
    ckv_to_bc_id_mapping = bc_integration.get_ckv_to_bc_id_mapping()
    if not isinstance(entity_conf,dict):
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

def _get_from_dict(data_dict, map_list):
    return reduce(operator.getitem, map_list, data_dict)


def _set_in_dict(data_dict, map_list, value):
    _get_from_dict(data_dict, map_list[:-1])[map_list[-1]] = value


def find_lines(node, kv):
    if isinstance(node, str):
        return node
    if isinstance(node, list):
        for i in node:
            for x in find_lines(i, kv):
                yield x
    elif isinstance(node, dict):
        if kv in node:
            yield node[kv]
        for j in node.values():
            for x in find_lines(j, kv):
                yield x


def _is_invalid_k8_definition(definition: dict) -> bool:
    return isinstance(definition, dict) and 'apiVersion' not in definition.keys() and 'kind' not in \
           definition.keys()
