from __future__ import annotations

import itertools
import logging
import operator
from functools import reduce
from typing import List, Tuple, Optional, Generator, Any

from checkov.common.bridgecrew.integration_features.features.policy_metadata_integration import integration as metadata_integration
from checkov.common.typing import _SkippedCheck
from checkov.common.util.suppression import collect_suppressions_for_context

ENDLINE = "__endline__"
STARTLINE = "__startline__"


class ContextParser:
    """
    CloudFormation template context parser
    """

    def __init__(self, cf_file: str, cf_template: dict[str, Any], cf_template_lines: List[Tuple[int, str]]) -> None:
        self.cf_file = cf_file
        self.cf_template = cf_template
        self.cf_template_lines = cf_template_lines

    def evaluate_default_refs(self) -> None:
        # Get Parameter Defaults - Locate Refs in Template
        refs = self.search_deep_keys("Ref", self.cf_template, [])

        for ref in refs:
            refname = ref.pop()
            ref.pop()  # Get rid of the 'Ref' dict key

            # TODO refactor into evaluations
            if not isinstance(refname, str):
                continue
            default_value = self.cf_template.get("Parameters", {}).get(refname, {}).get("Properties", {}).get("Default")
            if default_value is not None:
                logging.debug(
                    "Replacing Ref {} in file {} with default parameter value: {}".format(
                        refname, self.cf_file, default_value
                    )
                )
                self._set_in_dict(self.cf_template, ref, default_value)

                # TODO - Add Variable Eval Message for Output
                # Output in Checkov looks like this:
                # Variable versioning (of /.) evaluated to value "True" in expression: enabled = ${var.versioning}

    @staticmethod
    def extract_cf_resource_id(cf_resource: dict[str, Any], cf_resource_name: str) -> Optional[str]:
        if cf_resource_name == STARTLINE or cf_resource_name == ENDLINE:
            return None
        if "Type" not in cf_resource:
            # This is not a CloudFormation resource, skip
            return None
        return f"{cf_resource['Type']}.{cf_resource_name}"

    def extract_cf_resource_code_lines(
        self, cf_resource: dict[str, Any]
    ) -> Tuple[Optional[List[int]], Optional[List[Tuple[int, str]]]]:
        find_lines_result_set = set(self.find_lines(cf_resource, STARTLINE))
        if len(find_lines_result_set) >= 1:
            start_line = min(find_lines_result_set)
            end_line = max(self.find_lines(cf_resource, ENDLINE))

            # start_line - 2: -1 to switch to 0-based indexing, and -1 to capture the resource name
            entity_code_lines = self.cf_template_lines[start_line - 2 : end_line - 1]

            # if the file did not end in a new line, and this was the last resource in the file, then we
            # trimmed off the last line
            if (end_line - 1) < len(self.cf_template_lines) and not self.cf_template_lines[end_line - 1][1].endswith(
                "\n"
            ):
                entity_code_lines.append(self.cf_template_lines[end_line - 1])

            entity_code_lines = ContextParser.trim_lines(entity_code_lines)
            entity_lines_range = [entity_code_lines[0][0], entity_code_lines[-1][0]]
            return entity_lines_range, entity_code_lines
        return None, None

    @staticmethod
    def trim_lines(code_lines: List[Tuple[int, str]]) -> List[Tuple[int, str]]:
        # Removes leading and trailing lines that are only whitespace, returning a new value
        # The passed value should be a list of tuples of line numbers and line strings (entity_code_lines)
        start = 0
        end = len(code_lines)
        while start < end and not code_lines[start][1].strip():
            start += 1
        while end > start and not code_lines[end - 1][1].strip():
            end -= 1

        # if start == end, this will just be empty
        return code_lines[start:end]

    @staticmethod
    def find_lines(node: Any, kv: str) -> Generator[int, None, None]:
        # Hack to allow running checkov on json templates
        # CF scripts that are parsed using the yaml mechanism have a magic STARTLINE and ENDLINE property
        # CF scripts that are parsed using the json mechanism use dicts that have a marker
        if hasattr(node, "start_mark") and kv == STARTLINE:
            yield node.start_mark.line + 1

        if hasattr(node, "end_mark") and kv == ENDLINE:
            yield node.end_mark.line + 1

        if isinstance(node, list):
            for i in node:
                for x in ContextParser.find_lines(i, kv):
                    yield x
        elif isinstance(node, dict):
            if kv in node:
                yield node[kv]

    @staticmethod
    def collect_skip_comments(
        entity_code_lines: List[Tuple[int, str]], resource_config: dict[str, Any] | None = None
    ) -> List[_SkippedCheck]:
        skipped_checks = collect_suppressions_for_context(code_lines=entity_code_lines)

        bc_id_mapping = metadata_integration.bc_to_ckv_id_mapping
        if resource_config:
            metadata = resource_config.get("Metadata")
            if metadata:
                ckv_skip = metadata.get("checkov", {}).get("skip", [])
                bc_skip = metadata.get("bridgecrew", {}).get("skip", [])
                if ckv_skip or bc_skip:
                    for skip in itertools.chain(ckv_skip, bc_skip):
                        skip_id = skip.get("id")
                        skip_comment = skip.get("comment", "No comment provided")
                        if skip_id is None:
                            logging.warning("Check suppression is missing key 'id'")
                            continue

                        skipped_check: "_SkippedCheck" = {"id": skip_id, "suppress_comment": skip_comment}
                        if bc_id_mapping and skipped_check["id"] in bc_id_mapping:
                            skipped_check["bc_id"] = skipped_check["id"]
                            skipped_check["id"] = bc_id_mapping[skipped_check["id"]]
                        elif metadata_integration.check_metadata:
                            skipped_check["bc_id"] = metadata_integration.get_bc_id(skipped_check["id"])

                        skipped_checks.append(skipped_check)

        return skipped_checks

    @staticmethod
    def search_deep_keys(
        search_text: str, cfn_dict: str | list[Any] | dict[str, Any], path: list[int | str]
    ) -> list[list[int | str]]:
        """Search deep for keys and get their values"""
        keys: list[list[int | str]] = []
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
                    keys.extend(ContextParser.search_deep_keys(search_text, cfn_dict[key], pathprop))
                elif isinstance(cfn_dict[key], list):
                    for index, item in enumerate(cfn_dict[key]):
                        pathproparr = pathprop[:]
                        pathproparr.append(index)
                        keys.extend(ContextParser.search_deep_keys(search_text, item, pathproparr))
        elif isinstance(cfn_dict, list):
            for index, item in enumerate(cfn_dict):
                pathprop = list(path)
                pathprop.append(index)
                keys.extend(ContextParser.search_deep_keys(search_text, item, pathprop))

        return keys

    def _set_in_dict(self, data_dict: dict[str, Any], map_list: list[Any], value: str) -> None:
        v = self._get_from_dict(data_dict, map_list[:-1])
        # save the original marks so that we do not copy in the line numbers of the parameter element
        # but not all ref types will have these attributes
        start = None
        end = None
        if hasattr(v, "start_mark") and hasattr(v, "end_mark"):
            start = v.start_mark
            end = v.end_mark

        v[map_list[-1]] = value

        if hasattr(v[map_list[-1]], "start_mark") and start and end:
            v[map_list[-1]].start_mark = start
            v[map_list[-1]].end_mark = end

    @staticmethod
    def _get_from_dict(data_dict: dict[str, Any], map_list: list[Any]) -> list[Any] | dict[str, Any]:
        return reduce(operator.getitem, map_list, data_dict)
