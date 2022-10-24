from __future__ import annotations

from typing import TYPE_CHECKING, Any

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.parsers.yaml.parser import parse
from checkov.common.runners.object_runner import Runner as ObjectRunner

if TYPE_CHECKING:
    from checkov.common.checks.base_check_registry import BaseCheckRegistry


class Runner(ObjectRunner):
    check_type = CheckType.YAML  # noqa: CCE003  # a static attribute

    def __init__(self) -> None:
        super().__init__()
        self.file_extensions = ['.yaml', '.yml']

    def import_registry(self) -> BaseCheckRegistry:
        from checkov.yaml_doc.registry import registry

        return registry

    def _parse_file(
        self, f: str, file_content: str | None = None
    ) -> tuple[dict[str, Any] | list[dict[str, Any]], list[tuple[int, str]]] | None:
        return parse(f, file_content)

    def get_start_end_lines(
        self, end: int, result_config: dict[str, Any] | list[dict[str, Any]], start: int
    ) -> tuple[int, int]:
        if result_config and isinstance(result_config, list):
            if not isinstance(result_config[0], dict):
                return -1, -1
            start = result_config[0]["__startline__"] - 1
            end = result_config[len(result_config) - 1]["__endline__"]
        elif result_config and isinstance(result_config, dict):
            start = result_config["__startline__"]
            end = result_config["__endline__"]
        return end, start
