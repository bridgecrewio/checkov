from __future__ import annotations

from typing import Any

from checkov.common.checks.base_check_registry import BaseCheckRegistry
from checkov.common.output.report import CheckType
from checkov.common.parsers.json import parse
from checkov.common.parsers.node import DictNode
from checkov.common.runners.object_runner import Runner as ObjectRunner


class Runner(ObjectRunner):
    check_type = CheckType.JSON  # noqa: CCE003  # a static attribute

    def __init__(self) -> None:
        super().__init__()
        self.file_extensions = ['.json']

    def import_registry(self) -> BaseCheckRegistry:
        from checkov.json_doc.registry import registry
        return registry

    def _parse_file(  # type:ignore[override]  # expected behaviour but should be aligned
        self, f: str
    ) -> tuple[dict[str, Any] | list[dict[str, Any]] | None, list[tuple[int, str]] | None] | None:
        if not f.endswith(".json"):
            return None

        content: tuple[dict[str, Any] | list[dict[str, Any]] | None, list[tuple[int, str]] | None] = parse(f)
        return content

    def get_start_end_lines(self, end: int, result_config: dict[str, Any], start: int) -> tuple[int, int]:
        if not isinstance(result_config, DictNode):
            # shouldn't happen
            return 0, 0

        start = result_config.start_mark.line
        end = result_config.end_mark.line
        return end, start
