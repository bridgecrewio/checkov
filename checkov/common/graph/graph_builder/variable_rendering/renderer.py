import logging
import os
from typing import TYPE_CHECKING, List, Dict, Any
from abc import ABC, abstractmethod

from checkov.common.graph.graph_builder import Edge
from checkov.common.graph.graph_builder.utils import calculate_hash, run_function_multithreaded

if TYPE_CHECKING:
    from checkov.common.graph.graph_builder.local_graph import LocalGraph


class VariableRenderer(ABC):
    MAX_NUMBER_OF_LOOPS = 50

    def __init__(self, local_graph: "LocalGraph") -> None:
        self.local_graph = local_graph
        self.run_async = True if os.environ.get("RENDER_VARIABLES_ASYNC") == "True" else False
        self.max_workers = int(os.environ.get("RENDER_ASYNC_MAX_WORKERS", 50))
        self.done_edges_by_origin_vertex: Dict[int, List[Edge]] = {}
        self.replace_cache: List[Dict[str, Any]] = [{}] * len(local_graph.vertices)

    def render_variables_from_local_graph(self) -> None:
        # find vertices with out-degree = 0 and in-degree > 0
        end_vertices_indexes = self.local_graph.get_vertices_with_degrees_conditions(
            out_degree_cond=lambda degree: degree == 0, in_degree_cond=lambda degree: degree > 0
        )

        # all the edges entering `end_vertices`
        edges_to_render = self.local_graph.get_in_edges(end_vertices_indexes)
        loops = 0
        while len(edges_to_render) > 0:
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
                out_edges = self.local_graph.out_edges.get(origin_vertex_index, [])
                if all(e in self.done_edges_by_origin_vertex.get(origin_vertex_index, []) for e in out_edges):
                    end_vertices_indexes.append(origin_vertex_index)
            edges_to_render = self.local_graph.get_in_edges(end_vertices_indexes)
            edges_to_render = list(
                {
                    edge
                    for edge in edges_to_render
                    if edge not in self.done_edges_by_origin_vertex.get(edge.origin, [])
                }
            )
            loops += 1
            if loops >= self.MAX_NUMBER_OF_LOOPS:
                logging.warning(f"Reached 50 graph edge iterations, breaking.")
                break

        self.local_graph.update_vertices_configs()
        logging.info("done evaluating edges")
        self.evaluate_non_rendered_values()
        logging.info("done evaluate_non_rendered_values")

    def _edge_evaluation_task(self, edges: List[List[Edge]]) -> List[Edge]:
        inner_edges = edges[0]
        self.evaluate_vertex_attribute_from_edge(inner_edges)
        return inner_edges

    @abstractmethod
    def evaluate_vertex_attribute_from_edge(self, edge_list: List[Edge]) -> None:
        pass

    @staticmethod
    def group_edges_by_origin_and_label(edges: List[Edge]) -> List[List[Edge]]:
        edge_groups: Dict[str, List[Edge]] = {}
        for edge in edges:
            origin_and_label_hash = calculate_hash(f"{edge.origin}{edge.label}")
            edge_groups.setdefault(origin_and_label_hash, []).append(edge)
        return list(edge_groups.values())

    def evaluate_non_rendered_values(self) -> None:
        pass
