from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar, Any  # noqa

import rustworkx as rx

from checkov.common.graph.db_connectors.db_connector import DBConnector

if TYPE_CHECKING:
    from checkov.common.graph.graph_builder.graph_components.blocks import Block  # noqa
    from checkov.common.graph.graph_builder.local_graph import LocalGraph

_Block = TypeVar("_Block", bound="Block")


class RustworkxConnector(DBConnector["rx.PyDiGraph[Any, Any]"]):
    def __init__(self) -> None:
        self.graph = rx.PyDiGraph()  # type: ignore

    def save_graph(self, local_graph: LocalGraph[_Block], add_bulk_edges: bool = False) -> rx.PyDiGraph:  # type: ignore
        return self.rustworkx_from_local_graph(local_graph)

    def get_reader_endpoint(self) -> rx.PyDiGraph:  # type: ignore
        return self.graph

    def get_writer_endpoint(self) -> rx.PyDiGraph:  # type: ignore
        return self.graph

    def rustworkx_from_local_graph(self, local_graph: LocalGraph[_Block]) -> rx.PyDiGraph:  # type: ignore
        self.graph = rx.PyDiGraph()
        vertices_to_add = []
        for index, vertex in enumerate(local_graph.vertices):
            attr = vertex.get_attribute_dict()
            vertices_to_add.append((index, attr))

        edges_to_add = [
            (
                e.origin,
                e.dest,
                {"label": e.label, "source": e.origin, "target": e.dest},
            )
            for e in local_graph.edges
        ]

        self.graph.add_nodes_from(vertices_to_add)
        self.graph.add_edges_from(edges_to_add)

        return self.graph

    def disconnect(self) -> None:
        # not used, but is an abstractmethod
        return None
