from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any, Dict, List

from checkov.azure_pipelines.checks.registry import registry
from checkov.common.output.report import CheckType
from checkov.yaml_doc.runner import Runner as YamlRunner
from checkov.common.util.consts import START_LINE, END_LINE
from pathlib import Path


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

    def get_resource(self, file_path: str, key: str, supported_entities: Iterable[str],
                     definitions: dict[str, Any] | None = None, root_folder: str | Path | None = None) -> str:
        relative_file_path = f"/{os.path.relpath(file_path, root_folder)}"
        if not self.definitions or not isinstance(self.definitions, dict):
            return relative_file_path
        start_line, end_line = self.get_start_and_end_lines(key)
        resource_name = generate_resource_key_recursive(start_line, end_line, self.definitions[file_path])
        if not resource_name:
            return relative_file_path
        return f"{relative_file_path}:{resource_name}"


def generate_resource_key_recursive(start_line: int, end_line: int,
                                    conf: Dict[str, Any] | List[Dict[str, Any]], key: str | None = None
                                    ) -> str | None:
    if not isinstance(conf, dict):
        return key

    def _get_resource_from_dict(dict_to_inspect: dict[str, Any], key: str | None) -> str | None:
        if dict_to_inspect[START_LINE] <= start_line <= end_line <= dict_to_inspect[END_LINE]:
            job_name = dict_to_inspect.get('job', None)
            key = f'{key}.{job_name}' if job_name else key
            if dict_to_inspect[START_LINE] == start_line:
                return key
            return generate_resource_key_recursive(start_line, end_line, dict_to_inspect, key=key)
        return None

    for k, value in conf.items():
        if isinstance(value, dict):
            new_key = f'{key}.{k}' if key else k
            resource = _get_resource_from_dict(value, new_key)
            if resource:
                return resource
        elif isinstance(value, list):
            for i, e in enumerate(value):
                if isinstance(e, dict):
                    name = f'{k}[{i}]' if k != 'jobs' else k
                    new_key = f'{key}.{name}' if key else name
                    resource = _get_resource_from_dict(e, new_key)
                    if resource:
                        return resource
    return key
