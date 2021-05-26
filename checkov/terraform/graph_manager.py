import logging
from typing import List

from checkov.terraform.graph_builder.local_graph import LocalGraph
from checkov.terraform.parser import Parser


class GraphManager:
    def __init__(self, db_connector, source=''):
        self.db_connector = db_connector
        self.source = source

    def build_graph_from_source_directory(self, source_dir, render_variables=True, local_graph_class=LocalGraph,
                                          parsing_errors=None, download_external_modules=False, excluded_paths: List[str]=None):
        parser = Parser()
        logging.info('Parsing HCL files in source dir')
        module, module_dependency_map, tf_definitions = \
            parser.parse_hcl_module(source_dir, self.source, download_external_modules, parsing_errors, excluded_paths=excluded_paths)

        logging.info('Building graph from parsed module')
        local_graph = local_graph_class(module, module_dependency_map)
        local_graph.build_graph(render_variables=render_variables)

        return local_graph, tf_definitions

    def build_graph_from_tf_definitions(self, tf_definitions, render_variables=True):
        hcl_config_parser = Parser()
        module, module_dependency_map, _ = \
            hcl_config_parser.parse_hcl_module_from_tf_definitions(tf_definitions, '', self.source)
        local_graph = LocalGraph(module, module_dependency_map)
        local_graph.build_graph(render_variables=render_variables)

        return local_graph

    def save_graph(self, graph):
        return self.db_connector.save_graph(graph)

    def get_reader_traversal(self):
        return self.db_connector.get_reader_endpoint()

    def get_writer_traversal(self):
        return self.db_connector.get_writer_endpoint()

    def disconnect_from_db(self):
        self.db_connector.disconnect()
