from __future__ import annotations

from typing import cast, Any

from checkov.common.parsers.node import StrNode, ListNode
from checkov.common.util.consts import START_LINE, END_LINE, LINE_FIELD_NAMES
from checkov.common.util.suppression import collect_suppressions_for_report
from checkov.serverless.utils import ServerlessElements


def build_definitions_context(definitions: dict[str, dict[str, Any]], definitions_raw: dict[str, list[tuple[int, str]]]
                              ) -> dict[str, dict[str, Any]]:
    definitions_context: dict[str, dict[str, Any]] = {}
    for file_path, file_definitions in definitions.items():
        definitions_context[file_path] = {}
        for definition_attribute, definition_value in file_definitions.items():
            if definition_attribute not in [str(e) for e in ServerlessElements]:
                continue
            definitions_context[file_path][definition_attribute] = {}
            if isinstance(definition_value, dict):
                for resource_key, resource_attributes in definition_value.items():
                    add_resource_to_definitions_context(definitions_context, resource_key, resource_attributes,
                                                        definition_attribute, definitions_raw, file_path)
            elif isinstance(definition_value, list):
                for resource in definition_value:
                    add_resource_to_definitions_context(definitions_context, '', resource, definition_attribute,
                                                        definitions_raw, file_path)

            elif isinstance(definition_value, StrNode):
                add_resource_to_definitions_context(definitions_context, definition_attribute, definition_value,
                                                    definition_attribute,
                                                    definitions_raw, file_path)
    return definitions_context


def add_resource_to_definitions_context(definitions_context: dict[str, dict[str, Any]], resource_key: str,
                                        resource_attributes: dict[str, Any] | ListNode | StrNode, definition_attribute: str,
                                        definitions_raw: dict[str, Any], file_path: str) -> None:
    if resource_key in LINE_FIELD_NAMES:
        return

    if resource_attributes:
        if isinstance(resource_attributes, dict):
            start_line = resource_attributes[START_LINE] - 1
            end_line = resource_attributes[END_LINE] - 1
        elif isinstance(resource_attributes, ListNode):
            start_line = resource_attributes.start_mark.line
            end_line = resource_attributes.end_mark.line
        elif isinstance(resource_attributes, StrNode):
            start_line = resource_attributes.start_mark.line + 1
            end_line = resource_attributes.end_mark.line + 1
        else:
            return
    else:
        return

    definition_resource = {"start_line": start_line, "end_line": end_line}

    if resource_key is None and isinstance(resource_attributes, dict):
        resource_key = f"{resource_attributes.get('type')}.{resource_attributes.get('name')}"
    int_start_line = cast(int, definition_resource["start_line"])
    int_end_line = cast(int, definition_resource["end_line"])
    code_lines_for_suppressions_check = definitions_raw[file_path][int_start_line: int_end_line]
    definition_resource['skipped_checks'] = collect_suppressions_for_report(
        code_lines=code_lines_for_suppressions_check)
    if isinstance(resource_attributes, dict) and 'type' in resource_attributes:
        definition_resource["type"] = resource_attributes.get('type')

    definition_resource["code_lines"] = definitions_raw[file_path][start_line - 1: end_line]

    definitions_context[file_path][definition_attribute][resource_key] = definition_resource
