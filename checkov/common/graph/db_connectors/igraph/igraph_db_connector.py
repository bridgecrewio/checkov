from __future__ import annotations

import os
from random import randrange
from typing import TYPE_CHECKING, TypeVar

from igraph import Graph, plot

from checkov.common.graph.db_connectors.db_connector import DBConnector
from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.util.str_utils import strtobool

if TYPE_CHECKING:
    from checkov.common.graph.graph_builder.graph_components.blocks import Block  # noqa
    from checkov.common.graph.graph_builder.local_graph import LocalGraph

_Block = TypeVar("_Block", bound="Block")

PLOT_GRAPH = strtobool(os.getenv("CHECKOV_PLOT_GRAPH", "False"))
# possible layouts, except the 3D variants https://igraph.org/python/versions/latest/tutorial.html#layout-algorithms
PLOT_GRAPH_LAYOUT = os.getenv("CHECKOV_PLOT_GRAPH_LAYOUT", "kamada_kawai")
PLOT_RANDOM_COLORS = (
    "maroon",
    "red",
    "pink",
    "brown",
    "orange",
    "olive",
    "gold",
    "lime",
    "green",
    "teal",
    "cyan",
    "navy",
    "blue",
    "purple",
    "magenta",
    "black",
    "grey",
)
PLOT_RANDOM_COLORS_LEN = len(PLOT_RANDOM_COLORS)


class IgraphConnector(DBConnector[Graph]):
    def __init__(self) -> None:
        self.graph = Graph(directed=True)

    def save_graph(self, local_graph: LocalGraph[_Block], add_bulk_edges: bool = False) -> Graph:
        return self.igraph_from_local_graph(local_graph)

    def get_reader_endpoint(self) -> Graph:
        return self.graph

    def get_writer_endpoint(self) -> Graph:
        return self.graph

    def igraph_from_local_graph(self, local_graph: LocalGraph[_Block]) -> Graph:
        self.graph = Graph(directed=True)
        for index, vertex in enumerate(local_graph.vertices):
            attr = vertex.get_attribute_dict()
            vertex_attr = {
                "block_type_": vertex.block_type,
                "resource_type": attr[CustomAttributes.RESOURCE_TYPE] if CustomAttributes.RESOURCE_TYPE in attr else None,
                "attr": attr,
                "block_index": index,
            }
            if PLOT_GRAPH:
                vertex_attr["color"] = PLOT_RANDOM_COLORS[randrange(PLOT_RANDOM_COLORS_LEN)]
                vertex_attr["label"] = ".".join((attr[CustomAttributes.BLOCK_TYPE], attr[CustomAttributes.BLOCK_NAME]))

            self.graph.add_vertex(
                name=attr[CustomAttributes.HASH],
                **vertex_attr
            )

        edges_to_add = [
            (
                e.origin,
                e.dest,
            )
            for e in local_graph.edges
        ]
        edge_attributes = {
            "label": [e.label for e in local_graph.edges],
        }
        if PLOT_GRAPH:
            edge_colors = [PLOT_RANDOM_COLORS[randrange(PLOT_RANDOM_COLORS_LEN)] for _ in range(len(local_graph.edges))]
            edge_attributes["color"] = edge_colors
            edge_attributes["label_color"] = edge_colors

        self.graph.add_edges(edges_to_add, edge_attributes)

        if PLOT_GRAPH:
            graph_size = min(len(local_graph.vertices) * 100, 10_000)
            plot(
                self.graph,
                target=(f"graph_{local_graph.source}.png".lower()),
                bbox=(0, 0, graph_size, graph_size),
                margin=100,
                vertex_label_dist=2,
                layout=PLOT_GRAPH_LAYOUT,
            )

        return self.graph

    def disconnect(self) -> None:
        # not used, but is an abstractmethod
        return None
