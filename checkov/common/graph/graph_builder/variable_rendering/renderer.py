import logging
import os
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List, Dict, Any

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
        self._render_variables_from_edges()
        self._render_variables_from_vertices()

    def _render_variables_from_edges(self) -> None:
        # find vertices with out-degree = 0 and in-degree > 0
        end_vertices_indexes = self.local_graph.get_vertices_with_degrees_conditions(
            out_degree_cond=lambda degree: degree == 0, in_degree_cond=lambda degree: degree > 0
        )

        # all the edges entering `end_vertices`
        edges_to_render = self.local_graph.get_in_edges(end_vertices_indexes)
        end_vertices_indexes = []
        loops = 0
        previous_loops_mem = [[], []]
        duplicates_count = 0
        while len(edges_to_render) > 0:
            total_updated_values = 0
            print(f"evaluating {len(edges_to_render)} edges")
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
                    total_updated_values += self._edge_evaluation_task([edge_group])
            for edge in edges_to_render:
                origin = edge.origin
                self.done_edges_by_origin_vertex.setdefault(origin, []).append(edge)

            for edge in edges_to_render:
                origin_vertex_index = edge.origin
                out_edges = set(self.local_graph.out_edges.get(origin_vertex_index, []))
                done_edges_for_origin = self.done_edges_by_origin_vertex.get(origin_vertex_index, set())
                if out_edges.issubset(done_edges_for_origin):
                    end_vertices_indexes.append(origin_vertex_index)
            new_edges_to_render = self.local_graph.get_in_edges(end_vertices_indexes)
            print(f"total_updated_values = {total_updated_values}")
            edges_to_render = list(set(new_edges_to_render) - set(edges_to_render))

            two_iteration_ago_edges = previous_loops_mem[-2]
            previous_loops_mem.append(edges_to_render)
            intersection_edges = set(edges_to_render).intersection(two_iteration_ago_edges)
            match_percent = 0
            try:
                match_percent = int((len(intersection_edges)/len(edges_to_render))*100)
            except ZeroDivisionError:
                pass
            print(f"next round has {len(edges_to_render)} edges, two rounds ago it had {len(two_iteration_ago_edges)}, the size of intersection is {len(intersection_edges)} which is {match_percent}%")
            if match_percent > 90:
                duplicates_count += 1
            if duplicates_count > 5:
                logging.warning(f"Reached too many edge duplications. breaking.")
                break
            loops += 1
            if loops >= self.MAX_NUMBER_OF_LOOPS:
                logging.warning(f"Reached 50 graph edge iterations, breaking.")
                break

        self.local_graph.update_vertices_configs()
        logging.info("done evaluating edges")
        self.evaluate_non_rendered_values()
        logging.info("done evaluate_non_rendered_values")

    @abstractmethod
    def _render_variables_from_vertices(self) -> None:
        pass

    def _edge_evaluation_task(self, edges: List[List[Edge]]) -> int:
        inner_edges = edges[0]
        update_count = self.evaluate_vertex_attribute_from_edge(inner_edges)
        return update_count

    @abstractmethod
    def evaluate_vertex_attribute_from_edge(self, edge_list: List[Edge]) -> int:
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
