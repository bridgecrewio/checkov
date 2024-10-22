from __future__ import annotations

import logging
import operator
import re
from functools import reduce
from typing import Any, TYPE_CHECKING, Generator

from checkov.arm.utils import ArmElements
from checkov.common.bridgecrew.integration_features.features.policy_metadata_integration import integration as metadata_integration
from checkov.common.util.consts import LINE_FIELD_NAMES, START_LINE, END_LINE
from checkov.common.util.type_forcers import force_list

if TYPE_CHECKING:
    from checkov.common.typing import _SkippedCheck

COMMENT_REGEX = re.compile(r'([A-Z_\d]+)(:[^\n]+)?')
PARAMETERS_PATTERN = re.compile(r"\[parameters\('|'\)]")
VARIABLES_PATTERN = re.compile(r"\[variables\('|'\)]")


class ContextParser:
    """
    ARM template context parser
    """

    def __init__(self, arm_file: str, arm_template: dict[str, Any], arm_template_lines: list[tuple[int, str]]) -> None:
        self.arm_file = arm_file
        self.arm_template = arm_template
        self.arm_template_lines = arm_template_lines

    def evaluate_default_parameters(self) -> None:
        # Get parameter defaults and variable values
        parameter_defaults = {}
        if ArmElements.PARAMETERS in self.arm_template:
            for parameter, config in self.arm_template[ArmElements.PARAMETERS].items():
                if parameter in LINE_FIELD_NAMES:
                    continue
                if "defaultValue" in config:
                    parameter_defaults[parameter] = config["defaultValue"]

        variable_values = {}
        if ArmElements.VARIABLES in self.arm_template:
            for var, config in self.arm_template[ArmElements.VARIABLES].items():
                if var in LINE_FIELD_NAMES:
                    continue
                variable_values[var] = config

        # Find paths to substitute parameters and variables
        keys_w_params = self.search_deep_values('[parameters(', self.arm_template, [])
        keys_w_vars = self.search_deep_values('[variables(', self.arm_template, [])

        # Substitute Parameters and Variables
        for key_entry in keys_w_params:
            try:
                param = re.sub(
                    PARAMETERS_PATTERN,
                    "",
                    self._get_from_dict(dict(self.arm_template), key_entry[:-1])[key_entry[-1]],  # type:ignore[index]  # this will be a str
                )
                if param in parameter_defaults:
                    logging.debug(f"Replacing parameter {param} in file {self.arm_file} with default value: {parameter_defaults[param]}")
                    self._set_in_dict(dict(self.arm_template), key_entry, parameter_defaults[param])
            except TypeError:
                logging.debug(f"Failed to evaluate param in {self.arm_file}", exc_info=True)

        for key_entry in keys_w_vars:
            try:
                param = re.sub(
                    VARIABLES_PATTERN,
                    "",
                    self._get_from_dict(dict(self.arm_template), key_entry[:-1])[key_entry[-1]],  # type:ignore[index]  # this will be a str
                )
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
    def extract_arm_resource_id(arm_resource: dict[str, Any]) -> str | None:
        # if arm_resource_name == '__startline__' or arm_resource_name == '__endline__':
        #    return
        if 'type' not in arm_resource:
            # This is not an ARM resource, skip
            return None
        if 'name' not in arm_resource:
            # This is not an ARM resource, skip
            return None
        return f"{arm_resource['type']}.{arm_resource['name']}"

    @staticmethod
    def extract_arm_resource_name(arm_resource: dict[str, Any]) -> str | None:
        # if arm_resource_name == '__startline__' or arm_resource_name == '__endline__':
        #    return
        if 'name' not in arm_resource:
            # This is not an ARM resource, skip
            return None
        return f"{arm_resource['name']}"

    def extract_arm_resource_code_lines(
        self, arm_resource: dict[str, Any]
    ) -> tuple[list[int], list[tuple[int, str]]] | tuple[None, None]:
        find_lines_result_list = list(self.find_lines(arm_resource, START_LINE))
        if len(find_lines_result_list) >= 1:
            start_line = min(find_lines_result_list)
            end_line = max(list(self.find_lines(arm_resource, END_LINE)))

            entity_lines_range = [start_line, end_line]

            entity_code_lines = self.arm_template_lines[start_line - 1: end_line]
            return entity_lines_range, entity_code_lines
        return None, None

    @staticmethod
    def find_lines(node: dict[str, Any] | list[dict[str, Any]], kv: str) -> Generator[Any, None, None]:
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
    def collect_skip_comments(resource: dict[str, Any]) -> list[_SkippedCheck]:
        skipped_checks = []
        bc_id_mapping = metadata_integration.bc_to_ckv_id_mapping
        if "metadata" in resource:
            if "checkov" in resource["metadata"]:
                for item in force_list(resource["metadata"]["checkov"]):
                    skip_search = re.search(COMMENT_REGEX, str(item))
                    if skip_search:
                        skipped_check: "_SkippedCheck" = {
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
    def search_deep_keys(search_text: str, arm_dict: dict[str, Any], path: list[str | int]) -> list[list[Any]]:
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
    def search_deep_values(search_text: str, arm_dict: dict[str, Any], path: list[str | int]) -> list[list[str | int]]:
        """Search deep for keys with values matching search text"""
        keys: "list[list[str | int]]" = []
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

        for inner_keys in keys[:]:
            for i in inner_keys:
                if isinstance(i, list) or isinstance(i, dict):
                    keys.remove(inner_keys)

            # Remove parameter
            if search_text in inner_keys[-1]:  # type:ignore[operator]  # this will be a str
                inner_keys.pop()

        return keys

    def _set_in_dict(self, data_dict: dict[str, Any], map_list: list[str | int], value: Any) -> None:
        self._get_from_dict(data_dict, map_list[:-1])[map_list[-1]] = value  # type:ignore[index]  # this will be a str

    @staticmethod
    def _get_from_dict(data_dict: dict[str, Any], map_list: list[str | int]) -> dict[str, Any]:
        return reduce(operator.getitem, map_list, data_dict)  # type:ignore[arg-type]  # this works, because of a deeper dict access
