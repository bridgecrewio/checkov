from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List

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

    def get_resource(self, file_path: str, key: str, supported_entities: Iterable[str],
                     definitions: dict[str, Any] | None = None) -> str:
        if not self.definitions or not isinstance(self.definitions, dict):
            return key
        start_line, end_line = self.get_start_and_end_lines(key)
        resource_name = generate_resource_key_recursive(start_line, end_line, self.definitions[file_path])
        return resource_name if resource_name else key


def generate_resource_key_recursive(start_line: int, end_line: int,
                                    file_conf: Dict[str, Any] | List[Dict[str, Any]], resource_key: str | None = None
                                    ) -> str | None:
    if not isinstance(file_conf, dict):
        return resource_key

    def _get_resource_from_code_block(block_to_inspect: dict[str, Any], inspected_key: str | None) -> str | None:
        if block_to_inspect[START_LINE] <= start_line <= end_line <= block_to_inspect[END_LINE]:
            block_name = block_to_inspect.get('displayName',
                                              block_to_inspect.get('name',
                                                                   block_to_inspect.get('job',
                                                                                        block_to_inspect.get('stage',
                                                                                                             False))))
            inspected_key = f'{inspected_key}({block_name})' if block_name else inspected_key
            if block_to_inspect[START_LINE] == start_line:
                return inspected_key
            return generate_resource_key_recursive(start_line, end_line, block_to_inspect, resource_key=inspected_key)
        return None

    for code_block_name, code_block in file_conf.items():
        if isinstance(code_block, dict):
            new_key = f'{resource_key}.{code_block_name}' if resource_key else code_block_name
            resource = _get_resource_from_code_block(code_block, new_key)
            if resource:
                return resource
        elif isinstance(code_block, list):
            for index, item in enumerate(code_block):
                if isinstance(item, dict):
                    resource_key_to_inspect = f'{resource_key}.{code_block_name}[{index}]' if resource_key else f'{code_block_name}[{index}]'
                    resource = _get_resource_from_code_block(item, resource_key_to_inspect)
                    if resource:
                        return resource
    return resource_key
