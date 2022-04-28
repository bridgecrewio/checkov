from __future__ import annotations

from pathlib import Path
from typing import Type, TYPE_CHECKING

from pycep.typing import BicepJson

from checkov.bicep.parser import Parser
from checkov.bicep.utils import get_scannable_file_paths
from checkov.common.graph.db_connectors.db_connector import DBConnector
from checkov.common.graph.graph_manager import GraphManager
from checkov.bicep.graph_builder.local_graph import BicepLocalGraph

if TYPE_CHECKING:
    from checkov.common.graph.graph_builder.local_graph import LocalGraph


class BicepGraphManager(GraphManager):
    def __init__(self, db_connector: DBConnector, source: str = "Bicep") -> None:
        super().__init__(db_connector=db_connector, parser=None, source=source)

    def build_graph_from_source_directory(
        self,
        source_dir: str,
        render_variables: bool = True,
        local_graph_class: Type[LocalGraph] = BicepLocalGraph,
        parsing_errors: dict[str, Exception] | None = None,
        download_external_modules: bool = False,
        excluded_paths: list[str] | None = None,
    ) -> tuple[LocalGraph, dict[Path, BicepJson]]:
        file_paths = get_scannable_file_paths(root_folder=source_dir)
        definitions, definitions_raw, parsing_errors = Parser().get_files_definitions(file_paths)  # type:ignore[assignment]
        local_graph = self.build_graph_from_definitions(definitions)

        return local_graph, definitions

    def build_graph_from_definitions(
        self, definitions: dict[Path, BicepJson], render_variables: bool = True
    ) -> BicepLocalGraph:
        local_graph = BicepLocalGraph(definitions)
        local_graph.build_graph(render_variables)
        return local_graph
