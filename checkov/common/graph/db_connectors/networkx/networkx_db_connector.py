import networkx as nx

from checkov.common.graph.db_connectors.db_connector import DBConnector
from checkov.common.graph.graph_builder import CustomAttributes


class NetworkxConnector(DBConnector):
    def __init__(self):
        self.graph = nx.DiGraph()

    def save_graph(self, local_graph, add_bulk_edges=False):
        return self.networkx_from_local_graph(local_graph)

    def get_reader_endpoint(self):
        return self.graph

    def get_writer_endpoint(self):
        return self.graph

    def networkx_from_local_graph(self, local_graph):
        self.graph = nx.DiGraph()
        vertices_attributes = [v.get_decoded_attribute_dict() for v in local_graph.vertices]
        vertices_to_add = [(attr[CustomAttributes.HASH], attr) for attr in vertices_attributes]
        edges_to_add = [(vertices_attributes[e.origin][CustomAttributes.HASH], vertices_attributes[e.dest][CustomAttributes.HASH], {'label': e.label}) for e in local_graph.edges]

        self.graph.add_nodes_from(vertices_to_add)
        self.graph.add_edges_from(edges_to_add)

        return self.graph
