from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any

from checkov.azure_pipelines.checks.registry import registry
from checkov.common.output.report import CheckType
from checkov.yaml_doc.runner import Runner as YamlRunner
from checkov.common.util.consts import START_LINE, END_LINE


if TYPE_CHECKING:
    from checkov.common.checks.base_check_registry import BaseCheckRegistry
    from collections.abc import Iterable


class Runner(YamlRunner):
    check_type = CheckType.AZURE_PIPELINES  # noqa: CCE003  # a static attribute

    def require_external_checks(self) -> bool:
        return False

    def import_registry(self) -> BaseCheckRegistry:
        return registry

    def _parse_file(
        self, f: str, file_content: str | None = None
    ) -> tuple[dict[str, Any] | list[dict[str, Any]], list[tuple[int, str]]] | None:
        if self.is_workflow_file(f):
            return super()._parse_file(f=f)

        return None

    def is_workflow_file(self, file_path: str) -> bool:
        return file_path.endswith(('azure-pipelines.yml', 'azure-pipelines.yaml'))

    def get_resource(self, file_path: str, key: str, supported_entities: Iterable[str], definitions: dict[str, Any]|None = None, root_folder: str | None = None) -> str:
        relative_file_path = f"/{os.path.relpath(file_path, root_folder)}"
        if not self.definitions:
            return relative_file_path
        start_line, end_line = Runner.get_start_and_end_lines(key)
        resource_name = generate_resource_key_recursive(start_line, end_line, self.definitions[file_path])
        if not resource_name:
            return relative_file_path
        return f"{relative_file_path}:{resource_name}"

    @staticmethod
    def get_start_and_end_lines(key: str) -> list[int]:
        check_name = key.split('.')[-1]
        if "[" not in check_name or "[]" in check_name:
            return [-1, -1]

        start_end_line_bracket_index = check_name.index('[')

        return [int(x) for x in check_name[start_end_line_bracket_index + 1: len(check_name) - 1].split(':')]


def generate_resource_key_recursive(start_line, end_line, conf, key=None):
    if not isinstance(conf, dict):
        return key
    def _get_resource_from_dict(dict_to_inspect, key) -> str | None:
        if dict_to_inspect[START_LINE] <= start_line <= end_line <= dict_to_inspect[END_LINE]:
            if dict_to_inspect[START_LINE] == start_line:
                name = dict_to_inspect[list(dict_to_inspect.keys())[0]]
                return f'{key}.{name}' if key else f'{name}'
            return generate_resource_key_recursive(start_line, end_line, dict_to_inspect, key=key)
        return None

    for k, value in conf.items():
        if isinstance(value, dict):
            new_key = f'{key}.{k}' if key else k
            resource = _get_resource_from_dict(value, new_key)
            if resource and resource != new_key:
                return resource
            continue
        if isinstance(value, list):
            for e in value:
                if isinstance(e, dict):
                    new_key = f'{key}.{k}' if key else k
                    resource = _get_resource_from_dict(e, new_key)
                    if resource and resource != new_key:
                        return resource
            continue
    return key
