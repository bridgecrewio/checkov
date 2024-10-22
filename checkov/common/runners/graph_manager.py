from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from checkov.common.runners.graph_builder.local_graph import ObjectLocalGraph
from checkov.common.graph.graph_manager import GraphManager

if TYPE_CHECKING:
    from checkov.common.typing import LibraryGraphConnector
    from checkov.common.graph.graph_builder.graph_components.blocks import Block  # noqa


class ObjectGraphManager(GraphManager[ObjectLocalGraph, "dict[str | Path, dict[str, Any] | list[dict[str, Any]]]"]):
    def __init__(self, db_connector: LibraryGraphConnector, source: str) -> None:
        super().__init__(db_connector=db_connector, parser=None, source=source)

    def build_graph_from_source_directory(
        self,
        source_dir: str,
        local_graph_class: type[ObjectLocalGraph] = ObjectLocalGraph,
        render_variables: bool = True,
        parsing_errors: dict[str, Exception] | None = None,
        download_external_modules: bool = False,
        excluded_paths: list[str] | None = None,
    ) -> tuple[ObjectLocalGraph, dict[str | Path, dict[str, Any] | list[dict[str, Any]]]]:
        definitions = local_graph_class.get_files_definitions(root_folder=source_dir)
        local_graph = self.build_graph_from_definitions(definitions=definitions, graph_class=local_graph_class)

        return local_graph, definitions

    def build_graph_from_definitions(
        self,
        definitions: dict[str | Path, dict[str, Any] | list[dict[str, Any]]],
        render_variables: bool = False,
        graph_class: type[ObjectLocalGraph] = ObjectLocalGraph,
    ) -> ObjectLocalGraph:
        local_graph = graph_class(definitions)
        local_graph.build_graph(render_variables)
        return local_graph
