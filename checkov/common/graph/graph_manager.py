from __future__ import annotations

from abc import abstractmethod
from pathlib import Path
from typing import Type, Any, TYPE_CHECKING, TypeVar, Generic

from checkov.common.graph.db_connectors.db_connector import DBConnector

if TYPE_CHECKING:
    import networkx as nx
    from checkov.common.graph.graph_builder.local_graph import LocalGraph  # noqa
    from checkov.terraform.parser import Parser

_LocalGraph = TypeVar("_LocalGraph", bound="LocalGraph[Any]")


class GraphManager(Generic[_LocalGraph]):
    def __init__(self, db_connector: DBConnector[nx.DiGraph], parser: Parser | None, source: str = "") -> None:
        self.db_connector = db_connector
        self.source = source
        self.parser = parser

    @abstractmethod
    def build_graph_from_source_directory(
        self,
        source_dir: str,
        local_graph_class: Type[_LocalGraph],
        render_variables: bool = True,
        parsing_errors: dict[str, Exception] | None = None,
        download_external_modules: bool = False,
        excluded_paths: list[str] | None = None,
    ) -> tuple[_LocalGraph, dict[str, dict[str, Any]]]:
        pass

    @abstractmethod
    def build_graph_from_definitions(
        self, definitions: dict[str | Path, dict[str, Any]], render_variables: bool = True
    ) -> _LocalGraph:
        pass

    def save_graph(self, graph: _LocalGraph) -> nx.DiGraph:
        return self.db_connector.save_graph(graph)

    def get_reader_endpoint(self) -> nx.DiGraph:
        return self.db_connector.get_reader_endpoint()

    def get_writer_endpoint(self) -> nx.DiGraph:
        return self.db_connector.get_writer_endpoint()

    def disconnect_from_db(self) -> None:
        self.db_connector.disconnect()
