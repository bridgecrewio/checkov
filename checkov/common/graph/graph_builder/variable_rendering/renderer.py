from __future__ import annotations

import logging
import os
import warnings
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List, Dict, Any, Iterable, TypeVar, Generic

from checkov.common.graph.graph_builder import Edge
from checkov.common.graph.graph_builder.utils import run_function_multithreaded
from checkov.common.graph.graph_builder.graph_components.block_types import BlockType


if TYPE_CHECKING:
    from checkov.common.graph.graph_builder.graph_components.blocks import Block  # noqa
    from checkov.common.graph.graph_builder.local_graph import LocalGraph  # noqa

_LocalGraph = TypeVar("_LocalGraph", bound="LocalGraph[Any]")


class VariableRenderer(ABC, Generic[_LocalGraph]):
    MAX_NUMBER_OF_LOOPS = 50

    def __init__(self, local_graph: _LocalGraph) -> None:
        warnings.filterwarnings("ignore", category=SyntaxWarning)
        self.local_graph = local_graph
        self.run_async = True if os.getenv("RENDER_VARIABLES_ASYNC") == "True" else False
        self.max_workers = int(os.getenv("RENDER_ASYNC_MAX_WORKERS", 50))
        self.duplicate_percent = int(os.getenv("RENDER_EDGES_DUPLICATE_PERCENT", 90))
        self.duplicate_iter_count = int(os.getenv("RENDER_EDGES_DUPLICATE_ITER_COUNT", 4))
        self.done_edges_by_origin_vertex: Dict[int, List[Edge]] = {}
        self.replace_cache: List[Dict[str, Any]] = [{}] * len(local_graph.vertices)
        self.vertices_index_to_render: List[int] = []

    def render_variables_from_local_graph(self) -> None:
        self._render_variables_from_edges()
        self._render_variables_from_vertices()

    def _render_variables_from_edges(self) -> None:
        end_vertices_indexes = self._get_initial_end_vertices()
        edges_to_render = self.local_graph.get_in_edges(end_vertices_indexes)
        if self.vertices_index_to_render:
            edges_to_render = self._remove_unrelated_edges(edges_to_render)

        end_vertices_indexes = set()
        loops = 0
        evaluated_edges_cache: list[list[Edge]] = [[], []]
        duplicates_count = 0

        while edges_to_render:
            evaluated_edges_two_iter_ago = evaluated_edges_cache[-2]
            intersection_edges = set(edges_to_render).intersection(evaluated_edges_two_iter_ago)
            match_percent = int((len(intersection_edges) / len(edges_to_render)) * 100)
            if match_percent > self.duplicate_percent:
                duplicates_count += 1
            if duplicates_count > self.duplicate_iter_count:
                logging.info(f"Reached too many edge duplications of {self.duplicate_percent}% for {self.duplicate_iter_count} iterations. breaking.")
                break
            evaluated_edges_cache.append(edges_to_render)
            logging.debug(f"evaluating {len(edges_to_render)} edges; loop_num={loops}")

            edges_groups = self.group_edges_by_origin_and_label(edges_to_render)

            self._evaluate_edge_groups(edges_groups)

            self._update_done_edges_by_origin_vertex(edges_to_render)

            self._update_end_vertices_indexes(edges_to_render, end_vertices_indexes)

            new_edges_to_render = self.local_graph.get_in_edges_deduped(end_vertices_indexes)

            edges_to_render = self.local_graph.sort_edged_by_dest_out_degree(
                new_edges_to_render - set(edges_to_render)
            )

            loops += 1
            if loops >= self.MAX_NUMBER_OF_LOOPS:
                logging.warning(f"Reached max ({self.MAX_NUMBER_OF_LOOPS}) graph edge evaluation loops, breaking.")
                break

        if self.vertices_index_to_render:
            return
        self.local_graph.update_vertices_configs()
        logging.debug("done evaluating edges")
        self.evaluate_non_rendered_values()
        logging.debug("done evaluate_non_rendered_values")

    def _get_initial_end_vertices(self) -> set[int]:
        return self.local_graph.get_vertices_with_degrees_conditions(
            out_degree_cond=lambda d: d == 0,
            in_degree_cond=lambda d: d > 0,
        )

    def _evaluate_edge_groups(self, edges_groups: list[list[Edge]]) -> None:
        if self.run_async:
            run_function_multithreaded(
                func=self._edge_evaluation_task,
                data=edges_groups,
                max_group_size=1,
                num_of_workers=self.max_workers,
            )
        else:
            for edge_group in edges_groups:
                self._edge_evaluation_task([edge_group])

    def _update_done_edges_by_origin_vertex(self, edges_to_render: list[Edge]) -> None:
        for edge in edges_to_render:
            origin = edge.origin
            self.done_edges_by_origin_vertex.setdefault(origin, []).append(edge)

    def _update_end_vertices_indexes(self, edges_to_render: list[Edge], end_vertices_indexes: set[int]) -> None:
        already_checked: set[int] = set()

        for edge in edges_to_render:
            origin_vertex_index = edge.origin

            # Only check each origin once
            if origin_vertex_index in already_checked:
                continue
            already_checked.add(origin_vertex_index)

            out_edges = set(self.local_graph.out_edges.get(origin_vertex_index, []))
            done_edges_for_origin = set(self.done_edges_by_origin_vertex.get(origin_vertex_index, []))

            if out_edges.issubset(done_edges_for_origin):
                end_vertices_indexes.add(origin_vertex_index)

    @abstractmethod
    def _render_variables_from_vertices(self) -> None:
        pass

    def _edge_evaluation_task(self, edges: List[List[Edge]]) -> List[Edge]:
        inner_edges = edges[0]
        self.evaluate_vertex_attribute_from_edge(inner_edges)
        return inner_edges

    def _remove_unrelated_edges(self, edges_to_render: List[Edge]) -> List[Edge]:
        new_edges_to_render = []
        for edge in edges_to_render:
            if not self.local_graph.vertices[edge.origin] == BlockType.RESOURCE or edge.origin not in self.vertices_index_to_render:
                new_edges_to_render.append(edge)
        return new_edges_to_render

    @abstractmethod
    def evaluate_vertex_attribute_from_edge(self, edge_list: List[Edge]) -> None:
        pass

    @staticmethod
    def group_edges_by_origin_and_label(edges: Iterable[Edge]) -> List[List[Edge]]:
        edge_groups: Dict[str, List[Edge]] = {}
        for edge in edges:
            edge_groups.setdefault(f"{edge.origin}{edge.label}", []).append(edge)
        return list(edge_groups.values())

    @abstractmethod
    def evaluate_non_rendered_values(self) -> None:
        pass
