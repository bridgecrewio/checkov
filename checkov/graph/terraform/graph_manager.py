from checkov.graph.db_connectors.networkx.networkx import NetworkxConnector
from checkov.graph.parser import TerraformGraphParser
from checkov.graph.terraform.graph_builder.local_graph import LocalGraph


class GraphManager:
    def __init__(self, source='', db_connector=None):
        if db_connector is None:
            db_connector = NetworkxConnector()
        self.db_connector = db_connector
        self.source = source

    def build_graph_from_source_directory(self, source_dir, render_variables=True):
        parser = TerraformGraphParser()
        module, module_dependency_map, tf_definitions = \
            parser.parse_hcl_module(source_dir, self.source)

        local_graph = LocalGraph(module, module_dependency_map)
        local_graph.build_graph(render_variables=render_variables)

        return local_graph, tf_definitions

    def build_graph_from_tf_definitions(self, tf_definitions, render_variables=True):
        hcl_config_parser = TerraformGraphParser()
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
