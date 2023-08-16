from __future__ import annotations

from abc import abstractmethod
from typing import Type, TYPE_CHECKING, TypeVar, Generic, Any

if TYPE_CHECKING:
    from checkov.common.graph.graph_builder.local_graph import LocalGraph  # noqa
    from checkov.terraform.tf_parser import TFParser
    from checkov.common.typing import LibraryGraph, LibraryGraphConnector

_LocalGraph = TypeVar("_LocalGraph", bound="LocalGraph[Any]")
_Definitions = TypeVar("_Definitions")


class GraphManager(Generic[_LocalGraph, _Definitions]):
    def __init__(self, db_connector: LibraryGraphConnector, parser: TFParser | None, source: str = "") -> None:
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
    ) -> tuple[_LocalGraph | None, _Definitions]:
        pass

    @abstractmethod
    def build_graph_from_definitions(
        self, definitions: _Definitions, render_variables: bool = True
    ) -> _LocalGraph:
        pass

    def save_graph(self, graph: _LocalGraph) -> LibraryGraph:
        return self.db_connector.save_graph(graph)

    def get_reader_endpoint(self) -> LibraryGraph:
        return self.db_connector.get_reader_endpoint()

    def get_writer_endpoint(self) -> LibraryGraph:
        return self.db_connector.get_writer_endpoint()

    def disconnect_from_db(self) -> None:
        self.db_connector.disconnect()
