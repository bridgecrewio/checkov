from __future__ import annotations

import logging
from abc import abstractmethod
from pathlib import Path
from typing import Any

from checkov.common.graph.graph_builder import Edge
from checkov.common.graph.graph_builder.graph_components.blocks import Block
from checkov.common.graph.graph_builder.local_graph import LocalGraph


class ObjectLocalGraph(LocalGraph[Block]):
    def __init__(self, definitions: dict[str | Path, dict[str, Any] | list[dict[str, Any]]]) -> None:
        super().__init__()
        self.vertices: list[Block] = []
        self.definitions = definitions
        self.vertices_by_path_and_name: dict[tuple[str, str], int] = {}

    def build_graph(self, render_variables: bool = False) -> None:
        self._create_vertices()
        logging.debug(f"[{self.__class__.__name__}] created {len(self.vertices)} vertices")

        for i, vertex in enumerate(self.vertices):
            self.vertices_by_block_type[vertex.block_type].append(i)
            self.vertices_block_name_map[vertex.block_type][vertex.name].append(i)
            self.vertices_by_path_and_name[(vertex.path, vertex.name)] = i

            self.in_edges[i] = []
            self.out_edges[i] = []

        self._create_edges()
        logging.debug(f"[{self.__class__.__name__}] created {len(self.edges)} edges")

    @abstractmethod
    def _create_vertices(self) -> None:
        pass

    @abstractmethod
    def _create_edges(self) -> None:
        pass

    def _create_edge(self, origin_vertex_index: int, dest_vertex_index: int, label: str = "default") -> None:
        if origin_vertex_index == dest_vertex_index:
            # this should not happen
            return

        edge = Edge(origin_vertex_index, dest_vertex_index, label)
        self.edges.append(edge)
        self.out_edges[origin_vertex_index].append(edge)
        self.in_edges[dest_vertex_index].append(edge)

    @staticmethod
    @abstractmethod
    def get_files_definitions(root_folder: str | Path) -> dict[str | Path, dict[str, Any] | list[dict[str, Any]]]:
        """This is temporary till I have a better idea"""
        pass
