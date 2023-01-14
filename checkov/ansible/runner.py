from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List

from checkov.ansible.checks.registry import registry
from checkov.common.output.report import CheckType
from checkov.yaml_doc.runner import Runner as YamlRunner
from checkov.common.util.consts import START_LINE, END_LINE

if TYPE_CHECKING:
    from checkov.common.checks.base_check_registry import BaseCheckRegistry
    from collections.abc import Iterable

TASK_NAME_PATTERN = re.compile(r"^\s*-\s+name:\s+", re.MULTILINE)


class Runner(YamlRunner):
    check_type = CheckType.ANSIBLE  # noqa: CCE003  # a static attribute

    def require_external_checks(self) -> bool:
        return False

    def import_registry(self) -> BaseCheckRegistry:
        return registry

    def _parse_file(
        self, f: str, file_content: str | None = None
    ) -> tuple[dict[str, Any] | list[dict[str, Any]], list[tuple[int, str]]] | None:
        content = self.get_relevant_file_content(file_path=f)
        if content:
            return super()._parse_file(f=f, file_content=content)

        return None

    def get_relevant_file_content(self, file_path: str) -> str | None:
        if not file_path.endswith((".yaml", ".yml")):
            return None

        content = Path(file_path).read_text()
        match_task_name = re.search(TASK_NAME_PATTERN, content)
        if match_task_name:
            # there are more files, which belong to an ansible playbook,
            # but we are currently only interested in 'tasks'
            return content

        return None

    def get_resource(
        self, file_path: str, key: str, supported_entities: Iterable[str], start_line: int = -1, end_line: int = -1
    ) -> str:
        if not self.definitions or not isinstance(self.definitions, dict):
            return key

        resource_name = self.generate_resource_key_recursive(start_line, end_line, self.definitions[file_path])
        return resource_name if resource_name else key

    def generate_resource_key_recursive(
        self,
        start_line: int,
        end_line: int,
        file_conf: dict[str, Any] | list[dict[str, Any]],
        resource_key: str | None = None,
    ) -> str | None:
        if not isinstance(file_conf, list):
            return resource_key

        for code_block in file_conf:
            if code_block[START_LINE] <= start_line <= end_line <= code_block[END_LINE]:
                if "tasks" in code_block:
                    for task in code_block["tasks"]:
                        if task[START_LINE] <= start_line <= end_line <= task[END_LINE]:
                            return f'task.{task.get("name") or "unknown"}'
                else:
                    return f'task.{code_block.get("name") or "unknown"}'

        return resource_key
