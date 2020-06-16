import logging
import operator
import os
from functools import reduce

from checkov.common.runners.base_runner import BaseRunner
from checkov.runner_filter import RunnerFilter
from checkov.common.output.record import Record
from checkov.common.output.report import Report
from checkov.serverless.parser.parser import parse
from checkov.kubernetes.registry import registry
from checkov.cloudformation.parser.node import dict_node

SLS_FILE_MASK = ["serverless.yml", "serverless.yaml"]


class Runner(BaseRunner):
    check_type = "serverless"

    def run(self, root_folder, external_checks_dir=None, files=None, runner_filter=RunnerFilter()):
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
                if file in SLS_FILE_MASK:
                    parse_result = parse(file)
                    if parse_result:
                        (definitions[file], definitions_raw[file]) = parse_result

        if root_folder:
            for root, d_names, f_names in os.walk(root_folder):
                for file in f_names:
                    if file in SLS_FILE_MASK:
                        full_path = os.path.join(root, file)
                        if 'node_modules' not in full_path and "/." not in full_path:
                            # skip temp directories
                            files_list.append(full_path)

            for file in files_list:
                relative_file_path = f'/{os.path.relpath(file, os.path.commonprefix((root_folder, file)))}'
                parse_result = parse(file)
                if parse_result:
                    (definitions[relative_file_path], definitions_raw[relative_file_path]) = parse_result

        # Filter out empty files that have not been parsed successfully
        definitions = {k: v for k, v in definitions.items() if v}
        definitions_raw = {k: v for k, v in definitions_raw.items() if k in definitions.keys()}

        for sls_file in definitions.keys():
            if isinstance(definitions[sls_file], dict_node):
                #TODO refactor cfn variable evaluation and reuse here
                pass

        return report


    def _search_deep_keys(self, search_text, k8n_dict, path):
        """Search deep for keys and get their values"""
        keys = []
        if isinstance(k8n_dict, dict):
            for key in k8n_dict:
                pathprop = path[:]
                pathprop.append(key)
                if key == search_text:
                    pathprop.append(k8n_dict[key])
                    keys.append(pathprop)
                    # pop the last element off for nesting of found elements for
                    # dict and list checks
                    pathprop = pathprop[:-1]
                if isinstance(k8n_dict[key], dict):
                    keys.extend(self._search_deep_keys(search_text, k8n_dict[key], pathprop))
                elif isinstance(k8n_dict[key], list):
                    for index, item in enumerate(k8n_dict[key]):
                        pathproparr = pathprop[:]
                        pathproparr.append(index)
                        keys.extend(self._search_deep_keys(search_text, item, pathproparr))
        elif isinstance(k8n_dict, list):
            for index, item in enumerate(k8n_dict):
                pathprop = path[:]
                pathprop.append(index)
                keys.extend(self._search_deep_keys(search_text, item, pathprop))

        return keys

def get_skipped_checks(entity_conf):
    skipped = []
    metadata = {}
    if not isinstance(entity_conf,dict):
        return skipped
    if entity_conf["kind"] == "containers" or entity_conf["kind"] == "initContainers":
        metadata = entity_conf["parent_metadata"]
    else:
        if "metadata" in entity_conf.keys():
            metadata = entity_conf["metadata"]
    if "annotations" in metadata.keys():
        for key in metadata["annotations"].keys():
            skipped_item = {}
            if "checkov.io/skip" in key or "bridgecrew.io/skip" in key:
                if "CKV_K8S" in metadata["annotations"][key]:
                    if "=" in metadata["annotations"][key]:
                        (skipped_item["id"], skipped_item["suppress_comment"]) = metadata["annotations"][key].split("=")
                    else:
                        skipped_item["id"] = metadata["annotations"][key]
                        skipped_item["suppress_comment"] = "No comment provided"
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


