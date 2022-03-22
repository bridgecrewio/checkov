import logging
import operator
import re
from functools import reduce

from checkov.common.bridgecrew.integration_features.features.policy_metadata_integration import integration as metadata_integration
from checkov.common.util.type_forcers import force_list

COMMENT_REGEX = re.compile(r'([A-Z_\d]+)(:[^\n]+)?')


class ContextParser(object):
    """
    ARM template context parser
    """

    def __init__(self, arm_file, arm_template, arm_template_lines):
        self.arm_file = arm_file
        self.arm_template = arm_template
        self.arm_template_lines = arm_template_lines

    def evaluate_default_parameters(self) -> None:
        # Get parameter defaults and variable values
        parameter_defaults = {}
        if 'parameters' in self.arm_template.keys():
            for parameter in self.arm_template['parameters']:
                if parameter == '__startline__' or parameter == '__endline__':
                    continue
                if 'defaultValue' in self.arm_template['parameters'][parameter].keys():
                    parameter_defaults[parameter] = self.arm_template['parameters'][parameter]["defaultValue"]

        variable_values = {}
        if 'variables' in self.arm_template.keys():
            for var in self.arm_template['variables']:
                if var == '__startline__' or var == '__endline__':
                    continue
                variable_values[var] = self.arm_template['variables'][var]

        # Find paths to substitute parameters and variables
        keys_w_params = []
        keys_w_params.extend(self.search_deep_values('[parameters(', self.arm_template, []))

        keys_w_vars = []
        keys_w_vars.extend(self.search_deep_values('[variables(', self.arm_template, []))

        # Substitute Parameters and Variables
        for key_entry in keys_w_params:
            try:
                param = re.sub(re.compile(r"\[parameters\('|'\)]"), "", self._get_from_dict(dict(self.arm_template),
                                                                                key_entry[:-1])[key_entry[-1]])
                if param in parameter_defaults:
                    logging.debug(f"Replacing parameter {param} in file {self.arm_file} with default value: {parameter_defaults[param]}")
                    self._set_in_dict(dict(self.arm_template), key_entry, parameter_defaults[param])
            except TypeError:
                logging.debug(f"Failed to evaluate param in {self.arm_file}", exc_info=True)

        for key_entry in keys_w_vars:
            try:
                param = re.sub(re.compile(r"\[variables\('|'\)]"), "", self._get_from_dict(dict(self.arm_template),
                                                                               key_entry[:-1])[key_entry[-1]])
                if param in variable_values.keys():
                    self._set_in_dict(dict(self.arm_template), key_entry, variable_values[param])
                    logging.debug(
                        "Replacing variable {} in file {} with default value: {}".format(param, self.arm_file,
                                                                                         variable_values[param]))
                else:
                    logging.debug("Variable {} not found in evaluated variables in file {}".format(param, self.arm_file))
            except TypeError:
                logging.debug(f"Failed to evaluate param in {self.arm_file}", exc_info=True)

    @staticmethod
    def extract_arm_resource_id(arm_resource):
        # if arm_resource_name == '__startline__' or arm_resource_name == '__endline__':
        #    return
        if 'type' not in arm_resource:
            # This is not an ARM resource, skip
            return
        if 'name' not in arm_resource:
            # This is not an ARM resource, skip
            return
        return f"{arm_resource['type']}.{arm_resource['name']}"

    @staticmethod
    def extract_arm_resource_name(arm_resource):
        # if arm_resource_name == '__startline__' or arm_resource_name == '__endline__':
        #    return
        if 'name' not in arm_resource:
            # This is not an ARM resource, skip
            return
        return f"{arm_resource['name']}"

    def extract_arm_resource_code_lines(self, arm_resource):
        find_lines_result_list = list(self.find_lines(arm_resource, '__startline__'))
        if len(find_lines_result_list) >= 1:
            start_line = min(find_lines_result_list)
            end_line = max(list(self.find_lines(arm_resource, '__endline__')))

            entity_lines_range = [start_line, end_line]

            entity_code_lines = self.arm_template_lines[start_line - 1: end_line]
            return entity_lines_range, entity_code_lines
        return None, None

    @staticmethod
    def find_lines(node, kv):
        if isinstance(node, list):
            for i in node:
                for x in ContextParser.find_lines(i, kv):
                    yield x
        elif isinstance(node, dict):
            if kv in node:
                yield node[kv]
            for j in node.values():
                for x in ContextParser.find_lines(j, kv):
                    yield x

    @staticmethod
    def collect_skip_comments(resource):
        skipped_checks = []
        bc_id_mapping = metadata_integration.bc_to_ckv_id_mapping
        if "metadata" in resource:
            if "checkov" in resource["metadata"]:
                for index, item in enumerate(force_list(resource["metadata"]["checkov"])):
                    skip_search = re.search(COMMENT_REGEX, str(item))
                    if skip_search:
                        skipped_check = {
                            'id': skip_search.group(1),
                            'suppress_comment': skip_search.group(2)[1:] if skip_search.group(
                                2) else "No comment provided"
                        }
                        if bc_id_mapping and skipped_check["id"] in bc_id_mapping:
                            skipped_check["bc_id"] = skipped_check["id"]
                            skipped_check["id"] = bc_id_mapping[skipped_check["id"]]
                        elif metadata_integration.check_metadata:
                            skipped_check["bc_id"] = metadata_integration.get_bc_id(skipped_check["id"])

                        skipped_checks.append(skipped_check)

        return skipped_checks

    @staticmethod
    def search_deep_keys(search_text, arm_dict, path):
        """Search deep for keys and get their values"""
        keys = []
        if isinstance(arm_dict, dict):
            for key in arm_dict:
                pathprop = path[:]
                pathprop.append(key)
                if key == search_text:
                    pathprop.append(arm_dict[key])
                    keys.append(pathprop)
                    # pop the last element off for nesting of found elements for
                    # dict and list checks
                    pathprop = pathprop[:-1]
                if isinstance(arm_dict[key], dict):
                    keys.extend(ContextParser.search_deep_keys(search_text, arm_dict[key], pathprop))
                elif isinstance(arm_dict[key], list):
                    for index, item in enumerate(arm_dict[key]):
                        pathproparr = pathprop[:]
                        pathproparr.append(index)
                        keys.extend(ContextParser.search_deep_keys(search_text, item, pathproparr))
        elif isinstance(arm_dict, list):
            for index, item in enumerate(arm_dict):
                pathprop = path[:]
                pathprop.append(index)
                keys.extend(ContextParser.search_deep_keys(search_text, item, pathprop))

        return keys

    @staticmethod
    def search_deep_values(search_text, arm_dict, path):
        """Search deep for keys with values matching search text"""
        keys = []
        if isinstance(arm_dict, dict):
            for key in arm_dict:
                pathprop = path[:]
                pathprop.append(key)

                if search_text in str(arm_dict[key]):
                    pathprop.append(arm_dict[key])
                    keys.append(pathprop)
                    # pop the last element off for nesting of found elements for
                    # dict and list checks
                    pathprop = pathprop[:-1]
                if isinstance(arm_dict[key], dict):
                    keys.extend(ContextParser.search_deep_values(search_text, arm_dict[key], pathprop))
                elif isinstance(arm_dict[key], list):
                    for index, item in enumerate(arm_dict[key]):
                        pathproparr = pathprop[:]
                        pathproparr.append(index)
                        keys.extend(ContextParser.search_deep_values(search_text, item, pathproparr))
        elif isinstance(arm_dict, list):
            for index, item in enumerate(arm_dict):
                pathprop = path[:]
                pathprop.append(index)
                keys.extend(ContextParser.search_deep_values(search_text, item, pathprop))

        for key in keys:
            for i in key:
                if isinstance(i, list) or isinstance(i, dict):
                    keys.remove(key)

            # Remove parameter
            if search_text in key[-1]:
                key.pop()

        return keys

    def _set_in_dict(self, data_dict, map_list, value):
        self._get_from_dict(data_dict, map_list[:-1])[map_list[-1]] = value

    @staticmethod
    def _get_from_dict(data_dict, map_list):
        return reduce(operator.getitem, map_list, data_dict)
