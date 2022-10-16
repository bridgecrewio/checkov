from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from checkov.common.graph.db_connectors.db_connector import DBConnector
from checkov.common.graph.graph_manager import GraphManager
from checkov.common.runners.graph_builder.local_graph import ObjectLocalGraph

if TYPE_CHECKING:
    import networkx as nx
    from checkov.common.graph.graph_builder.graph_components.blocks import Block  # noqa


class ObjectGraphManager(GraphManager[ObjectLocalGraph]):
    def __init__(self, db_connector: DBConnector[nx.DiGraph], source: str) -> None:
        super().__init__(db_connector=db_connector, parser=None, source=source)

    def build_graph_from_source_directory(
        self,
        source_dir: str,
        local_graph_class: type[ObjectLocalGraph] = ObjectLocalGraph,
        render_variables: bool = True,
        parsing_errors: dict[str, Exception] | None = None,
        download_external_modules: bool = False,
        excluded_paths: list[str] | None = None,
    ) -> tuple[ObjectLocalGraph, dict[str, dict[str, Any]]]:
        # needs some refactor of thr ObjectRunner to implement this
        pass

    def build_graph_from_definitions(  # type:ignore[override]  # need to revisit it after adding `Generic` to `definitions`
        self,
        definitions: dict[str | Path, dict[str, Any] | list[dict[str, Any]]],
        render_variables: bool = False,
        graph_class: type[ObjectLocalGraph] = ObjectLocalGraph,
    ) -> ObjectLocalGraph:
        local_graph = graph_class(definitions)
        local_graph.build_graph(render_variables)
        return local_graph
