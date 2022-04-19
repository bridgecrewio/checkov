from __future__ import annotations

from abc import abstractmethod
from pathlib import Path
from typing import Type, Any, TYPE_CHECKING

from checkov.common.graph.db_connectors.db_connector import DBConnector
from checkov.common.graph.graph_builder.local_graph import LocalGraph

if TYPE_CHECKING:
    import networkx as nx
    from checkov.terraform.parser import Parser


class GraphManager:
    def __init__(self, db_connector: DBConnector, parser: Parser | None, source: str = "") -> None:
        self.db_connector = db_connector
        self.source = source
        self.parser = parser

    @abstractmethod
    def build_graph_from_source_directory(
        self,
        source_dir: str,
        render_variables: bool = True,
        local_graph_class: Type[LocalGraph] = LocalGraph,
        parsing_errors: dict[str, Exception] | None = None,
        download_external_modules: bool = False,
        excluded_paths: list[str] | None = None,
    ) -> tuple[LocalGraph, dict[str, dict[str, Any]]]:
        pass

    @abstractmethod
    def build_graph_from_definitions(
        self, definitions: dict[str | Path, dict[str, Any]], render_variables: bool = True
    ) -> LocalGraph:
        pass

    def save_graph(self, graph: LocalGraph) -> nx.DiGraph:
        return self.db_connector.save_graph(graph)

    def get_reader_endpoint(self) -> nx.DiGraph:
        return self.db_connector.get_reader_endpoint()

    def get_writer_endpoint(self) -> nx.DiGraph:
        return self.db_connector.get_writer_endpoint()

    def disconnect_from_db(self) -> None:
        self.db_connector.disconnect()
