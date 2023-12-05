from __future__ import annotations

from typing import Any, TYPE_CHECKING

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.parsers.json import parse
from checkov.common.parsers.node import DictNode, ListNode
from checkov.common.runners.object_runner import Runner as ObjectRunner

if TYPE_CHECKING:
    from checkov.common.checks.base_check_registry import BaseCheckRegistry
    from checkov.common.typing import LibraryGraphConnector
    from checkov.common.runners.graph_builder.local_graph import ObjectLocalGraph
    from checkov.common.runners.graph_manager import ObjectGraphManager


class Runner(ObjectRunner):
    check_type = CheckType.JSON  # noqa: CCE003  # a static attribute

    def __init__(
        self,
        db_connector: LibraryGraphConnector | None = None,
        source: str = "json",
        graph_class: type[ObjectLocalGraph] | None = None,
        graph_manager: ObjectGraphManager | None = None,
    ) -> None:
        super().__init__(
            db_connector=db_connector,
            source=source,
            graph_class=graph_class,
            graph_manager=graph_manager,
        )
        self.file_extensions = ['.json']

    def import_registry(self) -> BaseCheckRegistry:
        from checkov.json_doc.registry import registry
        return registry

    @staticmethod
    def _parse_file(
        f: str, file_content: str | None = None
    ) -> tuple[dict[str, Any] | list[dict[str, Any]], list[tuple[int, str]]] | None:
        if not f.endswith(".json"):
            return None

        return parse(filename=f, file_content=file_content)

    def get_start_end_lines(self, end: int, result_config: dict[str, Any], start: int) -> tuple[int, int]:
        if not isinstance(result_config, (DictNode, ListNode)):
            # shouldn't happen
            return 0, 0

        start = result_config.start_mark.line
        end = result_config.end_mark.line
        return end, start
