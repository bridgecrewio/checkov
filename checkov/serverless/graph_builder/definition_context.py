from __future__ import annotations

from typing import cast, Any

from checkov.common.parsers.node import StrNode
from checkov.common.util.consts import START_LINE, END_LINE
from checkov.common.util.suppression import collect_suppressions_for_report
from checkov.serverless.utils import ServerlessElements


def build_definitions_context(definitions: dict[str, dict[str, Any]], definitions_raw: dict[str, list[tuple[int, str]]]
                              ) -> dict[str, dict[str, Any]]:
    definitions_context: dict[str, dict[str, Any]] = {}
    for file_path, file_definitions in definitions.items():
        definitions_context[file_path] = {}
        for definition_attribute, definition_value in file_definitions.items():
            if definition_attribute not in ServerlessElements._member_map_.values():
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
                                        resource_attributes: dict[str, Any] | StrNode, definition_attribute: str,
                                        definitions_raw: dict[str, Any], file_path: str) -> None:
    if not isinstance(resource_attributes, dict) and not isinstance(resource_attributes, StrNode):
        return

    start_line = None
    end_line = None

    if isinstance(resource_attributes, dict):
        start_line = resource_attributes[START_LINE]
        end_line = resource_attributes[END_LINE]

    elif isinstance(resource_attributes, StrNode):
        start_line = resource_attributes.start_mark.line
        end_line = resource_attributes.end_mark.line

    definition_resource = {}

    if resource_key is None and isinstance(resource_attributes, dict):
        resource_key = f"{resource_attributes.get('type')}.{resource_attributes.get('name')}"
    int_start_line = cast(int, start_line)
    int_end_line = cast(int, end_line)
    code_lines_for_suppressions_check = definitions_raw[file_path][int_start_line: int_end_line]
    definition_resource['skipped_checks'] = collect_suppressions_for_report(
        code_lines=code_lines_for_suppressions_check)
    if isinstance(resource_attributes, dict) and 'type' in resource_attributes:
        definition_resource["type"] = resource_attributes.get('type')

    definition_resource["code_lines"] = definitions_raw[file_path][start_line: end_line + 1]
    definition_resource["start_line"] = start_line + 1
    definition_resource["end_line"] = end_line + 1
    definitions_context[file_path][definition_attribute][resource_key] = definition_resource
