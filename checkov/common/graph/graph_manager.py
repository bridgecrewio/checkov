from abc import abstractmethod
from typing import List, Type, Optional, Dict, Tuple, Any

from checkov.common.graph.db_connectors.db_connector import DBConnector
from checkov.common.graph.graph_builder.local_graph import LocalGraph


class GraphManager:
    def __init__(self, db_connector: DBConnector, parser, source: str = "") -> None:
        self.db_connector = db_connector
        self.source = source
        self.parser = parser

    @abstractmethod
    def build_graph_from_source_directory(
        self,
        source_dir: str,
        render_variables: bool = True,
        local_graph_class: Type[LocalGraph] = LocalGraph,
        parsing_errors: Optional[Dict[str, Exception]] = None,
        download_external_modules: bool = False,
        excluded_paths: Optional[List[str]] = None,
    ) -> Tuple[LocalGraph, Dict[str, Dict[str, Any]]]:
        pass

    @abstractmethod
    def build_graph_from_definitions(
        self, definitions: Dict[str, Dict[str, Any]], render_variables: bool = True
    ) -> LocalGraph:
        pass

    def save_graph(self, graph):
        return self.db_connector.save_graph(graph)

    def get_reader_endpoint(self):
        return self.db_connector.get_reader_endpoint()

    def get_writer_endpoint(self):
        return self.db_connector.get_writer_endpoint()

    def disconnect_from_db(self):
        self.db_connector.disconnect()
