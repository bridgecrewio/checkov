import logging
import os

from checkov.cloudformation.checks.resource.registry import resource_registry
from checkov.common.output.record import Record
from checkov.common.output.report import Report
from checkov.cloudformation.parser import parse

from functools import reduce
import operator

CF_POSSIBLE_ENDINGS = [".yml", ".yaml", ".json", ".template"]


class Runner:
    check_type = "CloudFormation"

    def run(self, root_folder, external_checks_dir=None, files=None):
        report = Report(self.check_type)
        definitions = {}
        definitions_raw = {}
        parsing_errors = {}
        files_list = []
        if external_checks_dir:
            for directory in external_checks_dir:
                resource_registry.load_external_checks(directory)

        if files:
            for file in files:
                files_list.append(file)

        if root_folder:
            for file in os.listdir(root_folder):
                file_ending = os.path.splitext(file)[1]
                if file_ending in CF_POSSIBLE_ENDINGS:
                    files_list.append(os.path.join(root_folder, file))

        for file in files_list:
            relative_file_path = f'/{os.path.relpath(file,os.path.commonprefix((root_folder, file)))}'
            (definitions[relative_file_path], definitions_raw[relative_file_path]) = parse(file)

        for cf_file in definitions.keys():
            logging.debug("Template Dump for {}: {}".format(cf_file, definitions[cf_file], indent=2))

            # Get Parameter Defaults - Locate Refs in Template
            refs = []
            refs.extend(self._search_deep_keys('Ref', definitions[cf_file], []))

            for ref in refs:
                refname = ref.pop()
                ref.pop()  # Get rid of the 'Ref' dict key

                if 'Parameters' in definitions[cf_file].keys() and refname in definitions[cf_file][
                    'Parameters'].keys():
                    # TODO refactor into evaluations
                    if 'Default' in definitions[cf_file]['Parameters'][refname].keys():
                        logging.debug(
                            "Replacing Ref {} in file {} with default parameter value: {}".format(refname, cf_file,
                                                                                                  definitions[
                                                                                                      cf_file][
                                                                                                      'Parameters'][
                                                                                                      refname][
                                                                                                      'Default']))
                        _set_in_dict(definitions[cf_file], ref,
                                     definitions[cf_file]['Parameters'][refname]['Default'])

                        ## TODO - Add Variable Eval Message for Output
                        # Output in Checkov looks like this:
                        # Variable versioning (of /.) evaluated to value "True" in expression: enabled = ${var.versioning}

            for resource_name, resource in definitions[cf_file]['Resources'].items():
                if resource_name == '__startline__' or resource_name == '__endline__':
                    continue
                resource_id = f"{resource['Type']}.{resource_name}"

                ## TODO - Evaluate skipped_checks
                skipped_checks = {}

                results = resource_registry.scan(cf_file, {resource_name: resource},
                                                 skipped_checks)
                # TODO refactor into context parsing
                start_line = min(list(find_lines(resource, '__startline__')))
                end_line = max(list(find_lines(resource, '__endline__')))

                entity_lines_range = [start_line, end_line - 1]

                entity_code_lines = definitions_raw[cf_file][start_line - 1: end_line - 1]

                # TODO - Variable Eval Message!
                variable_evaluations = {}

                for check, check_result in results.items():
                    ### TODO - Need to get entity_code_lines and entity_lines_range
                    record = Record(check_id=check.id, check_name=check.name, check_result=check_result,
                                    code_block=entity_code_lines, file_path=cf_file,
                                    file_line_range=entity_lines_range,
                                    resource=resource_id, evaluations=variable_evaluations,
                                    check_class=check.__class__.__module__)
                    report.add_record(record=record)
        return report

    def _search_deep_keys(self, search_text, cfn_dict, path):
        """Search deep for keys and get their values"""
        keys = []
        if isinstance(cfn_dict, dict):
            for key in cfn_dict:
                pathprop = path[:]
                pathprop.append(key)
                if key == search_text:
                    pathprop.append(cfn_dict[key])
                    keys.append(pathprop)
                    # pop the last element off for nesting of found elements for
                    # dict and list checks
                    pathprop = pathprop[:-1]
                if isinstance(cfn_dict[key], dict):
                    keys.extend(self._search_deep_keys(search_text, cfn_dict[key], pathprop))
                elif isinstance(cfn_dict[key], list):
                    for index, item in enumerate(cfn_dict[key]):
                        pathproparr = pathprop[:]
                        pathproparr.append(index)
                        keys.extend(self._search_deep_keys(search_text, item, pathproparr))
        elif isinstance(cfn_dict, list):
            for index, item in enumerate(cfn_dict):
                pathprop = path[:]
                pathprop.append(index)
                keys.extend(self._search_deep_keys(search_text, item, pathprop))

        return keys


def _get_from_dict(data_dict, map_list):
    return reduce(operator.getitem, map_list, data_dict)


def _set_in_dict(data_dict, map_list, value):
    _get_from_dict(data_dict, map_list[:-1])[map_list[-1]] = value


def find_lines(node, kv):
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
