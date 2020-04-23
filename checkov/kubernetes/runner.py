import logging
import operator
import os
from functools import reduce

from checkov.common.output.record import Record
from checkov.common.output.report import Report
from checkov.kubernetes.parser.parser import parse
from checkov.kubernetes.registry import registry

K8_POSSIBLE_ENDINGS = [".yaml", ".yml", ".json"]


class Runner:
    check_type = "kubernetes"

    def run(self, root_folder, external_checks_dir=None, files=None):
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
                (definitions[file], definitions_raw[file]) = parse(file)

        if root_folder:
            for root, d_names, f_names in os.walk(root_folder):
                for file in f_names:
                    file_ending = os.path.splitext(file)[1]
                    if file_ending in K8_POSSIBLE_ENDINGS:
                        files_list.append(os.path.join(root, file))

            for file in files_list:
                relative_file_path = f'/{os.path.relpath(file, os.path.commonprefix((root_folder, file)))}'
                (definitions[relative_file_path], definitions_raw[relative_file_path]) = parse(file)

        # Filter out empty files that have not been parsed successfully, and filter out non-K8 template files
        #definitions = {k: v for k, v in definitions.items() if
        #               v and (v.__contains__("apiVersion") and v.__contains__("kind"))}
        #definitions_raw = {k: v for k, v in definitions_raw.items() if k in definitions.keys()}

        for k8_file in definitions.keys():
            for i in range(len(definitions[k8_file])):
                if (not 'apiVersion' in definitions[k8_file][i].keys()) and (not 'kind' in definitions[k8_file][i].keys()):
                    continue
                logging.debug("Template Dump for {}: {}".format(k8_file, definitions[k8_file][i], indent=2))

                entity_conf = definitions[k8_file][i]
                ## TODO - Evaluate skipped_checks
                skipped_checks = {}

                results = registry.scan(k8_file, entity_conf,
                                        skipped_checks)
                # TODO refactor into context parsing
                find_lines_result_list = list(find_lines(entity_conf, '__startline__'))
                start_line = entity_conf["__startline__"]
                end_line = entity_conf["__endline__"]

                if start_line == end_line:
                    entity_lines_range = [start_line, end_line]
                    entity_code_lines = definitions_raw[k8_file][start_line - 1: end_line]
                else:
                    entity_lines_range = [start_line, end_line - 1]
                    entity_code_lines = definitions_raw[k8_file][start_line - 1: end_line - 1]

                # TODO - Variable Eval Message!
                variable_evaluations = {}

                for check, check_result in results.items():
                    ### TODO - Need to get entity_code_lines and entity_lines_range
                    record = Record(check_id=check.id, check_name=check.name, check_result=check_result,
                                    code_block=entity_code_lines, file_path=k8_file,
                                    file_line_range=entity_lines_range,
                                    resource=check.get_resource_id(entity_conf), evaluations=variable_evaluations,
                                    check_class=check.__class__.__module__)
                    report.add_record(record=record)


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


Runner().run(root_folder="/Users/barak/Documents/dev/terraform-static-analysis/checkov/kubernetes/test")
