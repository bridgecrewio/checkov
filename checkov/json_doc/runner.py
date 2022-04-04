from __future__ import annotations

from typing import Any

from checkov.common.output.report import CheckType
from checkov.common.parsers.json import parse
from checkov.common.parsers.node import DictNode
from checkov.common.runners.object_runner import Runner as ObjectRunner
from checkov.json_doc.base_registry import Registry


class Runner(ObjectRunner):
    check_type = CheckType.JSON

    def import_registry(self) -> Registry:
        from checkov.json_doc.registry import registry
        return registry

    def _parse_file(self, f: str) -> tuple[dict[str, Any] | list[dict[str, Any]], list[tuple[int, str]]] | tuple[None, None]:
        content: tuple[dict[str, Any] | list[dict[str, Any]], list[tuple[int, str]]] | tuple[None, None] = parse(f)
        return content

    def get_start_end_lines(self, end: int, result_config: DictNode, start: int) -> tuple[int, int]:
        start = result_config.start_mark.line
        end = result_config.end_mark.line
        return end, start
