from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from checkov.serverless.graph_builder.local_graph import ServerlessLocalGraph
from checkov.common.graph.graph_builder.consts import GraphSource
from checkov.common.graph.graph_manager import GraphManager
from checkov.serverless.utils import get_scannable_file_paths, get_files_definitions

if TYPE_CHECKING:
    from checkov.common.typing import LibraryGraphConnector


class ServerlessGraphManager(GraphManager[ServerlessLocalGraph, "dict[str, dict[str, Any]]"]):
    def __init__(self, db_connector: LibraryGraphConnector, source: str = GraphSource.SERVERLESS) -> None:
        super().__init__(db_connector=db_connector, parser=None, source=source)

    def build_graph_from_source_directory(
        self,
        source_dir: str,
        local_graph_class: type[ServerlessLocalGraph] = ServerlessLocalGraph,
        render_variables: bool = False,
        parsing_errors: Optional[dict[str, Exception]] = None,
        download_external_modules: Optional[bool] = False,
        excluded_paths: Optional[list[str]] = None,
        **kwargs: Any,
    ) -> tuple[ServerlessLocalGraph, dict[str, dict[str, Any]]]:
        file_paths = get_scannable_file_paths(root_folder=source_dir, excluded_paths=excluded_paths)
        definitions, _ = get_files_definitions(files=file_paths)

        local_graph = self.build_graph_from_definitions(definitions=definitions)

        return local_graph, definitions

    def build_graph_from_definitions(
        self, definitions: dict[str, dict[str, Any]], render_variables: bool = True
    ) -> ServerlessLocalGraph:
        local_graph = ServerlessLocalGraph(definitions=definitions)
        local_graph.build_graph(render_variables=render_variables)

        return local_graph
