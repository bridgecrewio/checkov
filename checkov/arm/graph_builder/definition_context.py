from __future__ import annotations

from typing import cast, Dict, Any

from checkov.common.util.consts import START_LINE, END_LINE
from checkov.common.util.suppression import collect_suppressions_for_report


ARM_COMMENT = "//"
DEFINITIONS_KEYS = ["parameters", "resources"]


def build_definitions_context(definitions: dict[str, dict[str, Any]], definitions_raw: dict[str, list[tuple[int, str]]]
                              ) -> Dict[str, Dict[str, Any]]:
    definitions_context: Dict[str, Dict[str, Any]] = {}
    for file_path_object, file_path_definitions in definitions.items():
        file_path = str(file_path_object)
        definitions_context[file_path] = {}
        for definition_attribute, resources in file_path_definitions.items():
            if definition_attribute not in DEFINITIONS_KEYS:
                continue
            definitions_context[file_path][definition_attribute] = {}
            if isinstance(resources, dict):
                for resource_key, resource_attributes in resources.items():
                    if isinstance(resource_attributes, dict):
                        add_resource_to_definitions_context(definitions_context, resource_key, resource_attributes,
                                                            definition_attribute, definitions_raw, file_path)
            elif isinstance(resources, list):
                for resource in resources:
                    if isinstance(resource, dict):
                        add_resource_to_definitions_context(definitions_context, '', resource,
                                                            definition_attribute, definitions_raw, file_path)
    return definitions_context


def add_resource_to_definitions_context(definitions_context: dict[str, dict[str, Any]], resource_key: str,
                                        resource_attributes: dict[str, Any], definition_attribute: str,
                                        definitions_raw: dict[str, Any], file_path: str) -> None:
    start_line = resource_attributes[START_LINE]
    end_line = resource_attributes[END_LINE]
    definition_resource = {"start_line": start_line, "end_line": end_line}

    if definition_attribute == "resources":
        resource_key = f"{resource_attributes.get('type')}.{resource_attributes.get('name')}"
        int_start_line = cast(int, definition_resource["start_line"])
        int_end_line = cast(int, definition_resource["end_line"])
        code_lines_for_suppressions_check = definitions_raw[file_path][int_start_line: int_end_line]
        definition_resource['skipped_checks'] = collect_suppressions_for_report(
            code_lines=code_lines_for_suppressions_check)
    else:
        definition_resource["type"] = resource_attributes.get('type')

    definition_resource["code_lines"] = definitions_raw[file_path][start_line - 1: end_line]
    definitions_context[file_path][definition_attribute][resource_key] = definition_resource
