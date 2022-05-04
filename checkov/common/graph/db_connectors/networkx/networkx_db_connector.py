from __future__ import annotations

from typing import TYPE_CHECKING

import networkx as nx

from checkov.common.graph.db_connectors.db_connector import DBConnector
from checkov.common.graph.graph_builder import CustomAttributes

if TYPE_CHECKING:
    from checkov.common.graph.graph_builder.local_graph import LocalGraph


class NetworkxConnector(DBConnector[nx.DiGraph]):
    def __init__(self) -> None:
        self.graph = nx.DiGraph()

    def save_graph(self, local_graph: LocalGraph, add_bulk_edges: bool = False) -> nx.DiGraph:
        return self.networkx_from_local_graph(local_graph)

    def get_reader_endpoint(self) -> nx.DiGraph:
        return self.graph

    def get_writer_endpoint(self) -> nx.DiGraph:
        return self.graph

    def networkx_from_local_graph(self, local_graph: LocalGraph) -> nx.DiGraph:
        self.graph = nx.DiGraph()
        vertices_attributes = [v.get_attribute_dict() for v in local_graph.vertices]
        vertices_to_add = [(attr[CustomAttributes.HASH], attr) for attr in vertices_attributes]
        edges_to_add = [(vertices_attributes[e.origin][CustomAttributes.HASH], vertices_attributes[e.dest][CustomAttributes.HASH], {'label': e.label}) for e in local_graph.edges]

        self.graph.add_nodes_from(vertices_to_add)
        self.graph.add_edges_from(edges_to_add)

        return self.graph
