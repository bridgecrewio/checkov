from __future__ import annotations

import logging
import os
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List, Dict, Any, Iterable, TypeVar

from checkov.common.graph.graph_builder import Edge
from checkov.common.graph.graph_builder.utils import run_function_multithreaded

if TYPE_CHECKING:
    from checkov.common.graph.graph_builder.graph_components.blocks import Block  # noqa
    from checkov.common.graph.graph_builder.local_graph import LocalGraph

_Block = TypeVar("_Block", bound="Block")


class VariableRenderer(ABC):
    MAX_NUMBER_OF_LOOPS = 50

    def __init__(self, local_graph: LocalGraph[_Block]) -> None:
        self.local_graph = local_graph
        self.run_async = True if os.getenv("RENDER_VARIABLES_ASYNC") == "True" else False
        self.max_workers = int(os.getenv("RENDER_ASYNC_MAX_WORKERS", 50))
        self.duplicate_percent = int(os.getenv("RENDER_EDGES_DUPLICATE_PERCENT", 90))
        self.duplicate_iter_count = int(os.getenv("RENDER_EDGES_DUPLICATE_ITER_COUNT", 4))
        self.done_edges_by_origin_vertex: Dict[int, List[Edge]] = {}
        self.replace_cache: List[Dict[str, Any]] = [{}] * len(local_graph.vertices)

    def render_variables_from_local_graph(self) -> None:
        self._render_variables_from_edges()
        self._render_variables_from_vertices()

    def _render_variables_from_edges(self) -> None:
        # find vertices with out-degree = 0 and in-degree > 0
        end_vertices_indexes = self.local_graph.get_vertices_with_degrees_conditions(
            out_degree_cond=lambda degree: degree == 0, in_degree_cond=lambda degree: degree > 0
        )

        # all the edges entering `end_vertices`
        edges_to_render = self.local_graph.get_in_edges(end_vertices_indexes)
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

            logging.info(f"evaluating {len(edges_to_render)} edges")
            # group edges that have the same origin and label together
            edges_groups = self.group_edges_by_origin_and_label(edges_to_render)
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
            for edge in edges_to_render:
                origin = edge.origin
                self.done_edges_by_origin_vertex.setdefault(origin, []).append(edge)

            for edge in edges_to_render:
                origin_vertex_index = edge.origin
                out_edges = set(self.local_graph.out_edges.get(origin_vertex_index, []))
                done_edges_for_origin = self.done_edges_by_origin_vertex.get(origin_vertex_index, [])
                if out_edges.issubset(done_edges_for_origin):
                    end_vertices_indexes.add(origin_vertex_index)
            new_edges_to_render = self.local_graph.get_in_edges_deduped(end_vertices_indexes)
            edges_to_render = self.local_graph.sort_edged_by_dest_out_degree(
                new_edges_to_render - set(edges_to_render)
            )

            loops += 1
            if loops >= self.MAX_NUMBER_OF_LOOPS:
                logging.warning("Reached 50 graph edge iterations, breaking.")
                break

        self.local_graph.update_vertices_configs()
        logging.info("done evaluating edges")
        self.evaluate_non_rendered_values()
        logging.info("done evaluate_non_rendered_values")

    @abstractmethod
    def _render_variables_from_vertices(self) -> None:
        pass

    def _edge_evaluation_task(self, edges: List[List[Edge]]) -> List[Edge]:
        inner_edges = edges[0]
        self.evaluate_vertex_attribute_from_edge(inner_edges)
        return inner_edges

    @abstractmethod
    def evaluate_vertex_attribute_from_edge(self, edge_list: List[Edge]) -> None:
        pass

    @staticmethod
    def group_edges_by_origin_and_label(edges: Iterable[Edge]) -> List[List[Edge]]:
        edge_groups: Dict[str, List[Edge]] = {}
        for edge in edges:
            edge_groups.setdefault(f"{edge.origin}{edge.label}", []).append(edge)
        return list(edge_groups.values())

    def evaluate_non_rendered_values(self) -> None:
        pass
