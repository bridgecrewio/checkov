from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

from igraph import Graph

from checkov.common.graph.db_connectors.db_connector import DBConnector
from checkov.common.graph.graph_builder import CustomAttributes

if TYPE_CHECKING:
    from checkov.common.graph.graph_builder.graph_components.blocks import Block  # noqa
    from checkov.common.graph.graph_builder.local_graph import LocalGraph

_Block = TypeVar("_Block", bound="Block")


class IgraphConnector(DBConnector[Graph]):
    def __init__(self) -> None:
        self.graph = Graph(directed=True)

    def save_graph(self, local_graph: LocalGraph[_Block], add_bulk_edges: bool = False) -> Graph:
        return self.networkit_from_local_graph(local_graph)

    def get_reader_endpoint(self) -> Graph:
        return self.graph

    def get_writer_endpoint(self) -> Graph:
        return self.graph

    def networkit_from_local_graph(self, local_graph: LocalGraph[_Block]) -> Graph:
        # colors = {
        #     "Pod": "blue",
        #     "Deployment": "magenta",
        #     "Service": "olive",
        # }
        #
        # random_colors = ("red", "blue", "olive", "gold", "magenta", "purple", "black")
        # random_colors_len = len(random_colors)
        # randrange(len(random_colors))

        self.graph = Graph(directed=True)
        for index, vertex in enumerate(local_graph.vertices):
            attr = vertex.get_attribute_dict()
            self.graph.add_vertex(
                name=attr[CustomAttributes.HASH],
                block_type_=vertex.block_type,
                resource_type=attr[CustomAttributes.RESOURCE_TYPE] if CustomAttributes.RESOURCE_TYPE in attr else None,
                # label=attr[CustomAttributes.BLOCK_NAME],
                # color=colors.get(attr["kind"], "red"),
                attr=attr,
                block_index=index
            )

        edges_to_add = [
            (
                e.origin,
                e.dest,

            )
            for e in local_graph.edges
        ]
        # edge_colors = [random_colors[randrange(random_colors_len)] for _ in range(len(local_graph.edges))]
        edge_attributes = {
            "label": [e.label for e in local_graph.edges],
            # "color": edge_colors,
            # "label_color": edge_colors,
        }
        self.graph.add_edges(edges_to_add, edge_attributes)

        # plot(self.graph, target='myfile.png', bbox=(0, 0, 2000, 2000), margin=100, vertex_label_dist=1, layout="circle")
        return self.graph

    def disconnect(self) -> None:
        # not used, but is an abstractmethod
        return None
