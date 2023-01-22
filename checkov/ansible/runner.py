from __future__ import annotations

from typing import TYPE_CHECKING, Any

from checkov.ansible.checks.registry import registry
from checkov.ansible.graph_builder.graph_components.resource_types import ResourceType
from checkov.ansible.graph_builder.local_graph import AnsibleLocalGraph
from checkov.ansible.utils import TASK_RESERVED_KEYWORDS, get_relevant_file_content
from checkov.common.output.report import CheckType
from checkov.common.util.consts import START_LINE, END_LINE
from checkov.yaml_doc.runner import Runner as YamlRunner

if TYPE_CHECKING:
    from checkov.common.checks.base_check_registry import BaseCheckRegistry
    from checkov.common.typing import LibraryGraphConnector
    from checkov.common.runners.graph_builder.local_graph import ObjectLocalGraph
    from checkov.common.runners.graph_manager import ObjectGraphManager
    from collections.abc import Iterable


class Runner(YamlRunner):
    check_type = CheckType.ANSIBLE  # noqa: CCE003  # a static attribute

    def __init__(
        self,
        db_connector: LibraryGraphConnector | None = None,
        source: str = "Ansible",
        graph_class: type[ObjectLocalGraph] = AnsibleLocalGraph,
        graph_manager: ObjectGraphManager | None = None,
    ) -> None:
        super().__init__(
            db_connector=db_connector,
            source=source,
            graph_class=graph_class,
            graph_manager=graph_manager,
        )

    def require_external_checks(self) -> bool:
        return False

    def import_registry(self) -> BaseCheckRegistry:
        return registry

    def _parse_file(
        self, f: str, file_content: str | None = None
    ) -> tuple[dict[str, Any] | list[dict[str, Any]], list[tuple[int, str]]] | None:
        content = get_relevant_file_content(file_path=f)
        if content:
            return super()._parse_file(f=f, file_content=content)

        return None

    def get_resource(
        self, file_path: str, key: str, supported_entities: Iterable[str], start_line: int = -1, end_line: int = -1
    ) -> str:
        if not self.definitions or not isinstance(self.definitions, dict):
            return key

        resource_name = self.generate_resource_name(start_line, end_line, self.definitions[file_path])
        return resource_name if resource_name else key

    def generate_resource_name(
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
                if ResourceType.TASKS in code_block:
                    for task in code_block[ResourceType.TASKS]:
                        if task[START_LINE] <= start_line <= end_line <= task[END_LINE]:
                            return self._generate_resource_name(task) or resource_key
                else:
                    return self._generate_resource_name(code_block) or resource_key

        return resource_key

    def _generate_resource_name(self, task: dict[str, Any]) -> str | None:
        # grab the task name at the beginning before trying to find the actual module name
        task_name = task.get("name") or "unknown"

        for name in task:
            if name in TASK_RESERVED_KEYWORDS:
                continue

            return f"{ResourceType.TASKS}.{name}.{task_name}"

        return None
