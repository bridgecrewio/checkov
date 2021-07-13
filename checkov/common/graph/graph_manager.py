from abc import abstractmethod
from typing import List

from checkov.common.graph.graph_builder.local_graph import LocalGraph


class GraphManager:
    def __init__(self, db_connector, parser, source=''):
        self.db_connector = db_connector
        self.source = source
        self.parser = parser

    @abstractmethod
    def build_graph_from_source_directory(self, source_dir, render_variables=True, local_graph_class=LocalGraph,
                                          parsing_errors=None, download_external_modules=False, excluded_paths: List[str]=None):
        pass

    @abstractmethod
    def build_graph_from_definitions(self, definitions, render_variables=True):
        pass

    def save_graph(self, graph):
        return self.db_connector.save_graph(graph)

    def get_reader_endpoint(self):
        return self.db_connector.get_reader_endpoint()

    def get_writer_endpoint(self):
        return self.db_connector.get_writer_endpoint()

    def disconnect_from_db(self):
        self.db_connector.disconnect()
