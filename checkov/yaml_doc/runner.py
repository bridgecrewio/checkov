from __future__ import annotations

from typing import TYPE_CHECKING, Any

from checkov.common.output.report import CheckType
from checkov.common.parsers.yaml.parser import parse
from checkov.common.runners.object_runner import Runner as ObjectRunner

if TYPE_CHECKING:
    from checkov.common.checks.base_check_registry import BaseCheckRegistry


class Runner(ObjectRunner):
    check_type = CheckType.YAML

    def __init__(self) -> None:
        super().__init__()
        self.file_extensions = ['.yaml', '.yml']

    def import_registry(self) -> BaseCheckRegistry:
        from checkov.yaml_doc.registry import registry

        return registry

    def _parse_file(
        self, f: str
    ) -> tuple[dict[str, Any] | list[dict[str, Any]], list[tuple[int, str]]] | None:
        content: tuple[dict[str, Any] | list[dict[str, Any]], list[tuple[int, str]]] | None = parse(f)
        return content

    def get_start_end_lines(
        self, end: int, result_config: dict[str, Any] | list[dict[str, Any]], start: int
    ) -> tuple[int, int]:
        if result_config and isinstance(result_config, list):
            start = result_config[0]["__startline__"] - 1
            end = result_config[len(result_config) - 1]["__endline__"]
        elif result_config and isinstance(result_config, dict):
            start = result_config["__startline__"]
            end = result_config["__endline__"]
        return end, start
