from __future__ import annotations

import logging
import os
import sys
import warnings
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List, Dict, Any, Iterable, TypeVar, Generic, Set, Optional, Callable

from checkov.common.graph.graph_builder import Edge
from checkov.common.graph.graph_builder.deterministic import deterministic_graph_enabled, stable_key_cache_enabled
from checkov.common.graph.graph_builder.variable_rendering.affected_schedule import (
    EdgeSchedule,
    ScheduleUnsupported,
    affected_schedule_enabled,
    build_affected_schedule,
    schedule_verification_enabled,
)
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
        if deterministic_graph_enabled():
            # the duplicate-edge early stop is computed over the whole graph; see deterministic.py
            self.duplicate_iter_count = sys.maxsize
        self.done_edges_by_origin_vertex: Dict[int, List[Edge]] = {}
        self.replace_cache: List[Dict[str, Any]] = [{}] * len(local_graph.vertices)
        self.vertices_index_to_render: List[int] = []
        self.frozen_vertices: Set[int] = set()
        """Incremental mode only (set by checkov.terraform.graph_builder.incremental_graph): vertices already holding
        their final state. The edge loop keeps its full schedule but never evaluates an edge whose origin is frozen,
        and the post-loop passes skip frozen vertices."""
        self.on_edge_loop_end: Optional[Callable[[], None]] = None
        """Incremental mode only: called after the edge loop, before the post-loop passes (graph export)."""
        self.schedule_stats: Dict[str, Any] = {}
        """Incremental mode only: whether the affected-only edge schedule replaced the global loop, and its size."""

    def render_variables_from_local_graph(self) -> None:
        self._render_variables_from_edges()
        self._render_variables_from_vertices()

    def _render_variables_from_edges(self) -> None:
        if not self._render_edges_with_affected_schedule():
            self._run_edge_loop()

        if self.vertices_index_to_render:
            return
        if self.on_edge_loop_end is not None:
            self.on_edge_loop_end()
        if self.frozen_vertices:
            self.local_graph.update_vertices_configs(skip=self.frozen_vertices)
            logging.debug("done evaluating edges")
            self.evaluate_non_rendered_values()
            return
        self.local_graph.update_vertices_configs()
        logging.debug("done evaluating edges")
        self.evaluate_non_rendered_values()
        logging.debug("done evaluate_non_rendered_values")

    def _render_edges_with_affected_schedule(self) -> bool:
        """Incremental mode only: evaluate exactly what the global edge loop would evaluate, without running it over
        the whole graph (see affected_schedule.py). False when not applicable: the caller runs the global loop."""
        if not (self.frozen_vertices and deterministic_graph_enabled() and affected_schedule_enabled()):
            return False
        if self.run_async or self.vertices_index_to_render:
            return False
        initial_end = self._get_initial_end_vertices()
        try:
            schedule = build_affected_schedule(self.local_graph, self.frozen_vertices, initial_end,
                                               self.MAX_NUMBER_OF_LOOPS)
        except ScheduleUnsupported as error:
            logging.info(f"affected render schedule not applicable, running the global edge loop: {error}")
            self.schedule_stats = {"applied": False, "reason": str(error)}
            return False
        self.schedule_stats = {"applied": True, "loops": schedule.loops, "groups": schedule.groups,
                               "edges": schedule.edges}
        if schedule_verification_enabled():
            self._run_edge_loop_and_compare(schedule)
            return True
        if schedule.reached_cap:
            logging.warning(f"Reached max ({self.MAX_NUMBER_OF_LOOPS}) graph edge evaluation loops, breaking.")
        for groups in schedule.rounds:
            for group in groups:
                self._edge_evaluation_task([group])
        return True

    def _run_edge_loop_and_compare(self, schedule: EdgeSchedule) -> None:
        """Test mode: render with the global loop (real evaluations), and require that it evaluated exactly the
        computed schedule, in the same order."""
        trace: list[tuple[tuple[int, int, str], ...]] = []
        evaluate = self._edge_evaluation_task

        def recording_task(edges: List[List[Edge]]) -> List[Edge]:
            trace.append(tuple((e.origin, e.dest, e.label) for e in edges[0]))
            return evaluate(edges)

        self._edge_evaluation_task = recording_task  # type: ignore[method-assign]
        try:
            self._run_edge_loop()
        finally:
            del self._edge_evaluation_task
        self.schedule_stats["verified"] = trace == schedule.trace()
        if trace != schedule.trace():
            raise RuntimeError(f"affected render schedule differs from the global edge loop: "
                               f"{len(trace)} vs {len(schedule.trace())} evaluated groups")

    def _run_edge_loop(self) -> None:
        if not (deterministic_graph_enabled() and stable_key_cache_enabled()):
            self._run_global_edge_loop()
            return
        self.local_graph.stable_key_cache = {}
        try:
            self._run_global_edge_loop()
        finally:
            self.local_graph.stable_key_cache = None

    def _run_global_edge_loop(self) -> None:
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

    def _get_initial_end_vertices(self) -> set[int]:
        return self.local_graph.get_vertices_with_degrees_conditions(
            out_degree_cond=lambda d: d == 0,
            in_degree_cond=lambda d: d > 0,
        )

    def _evaluate_edge_groups(self, edges_groups: list[list[Edge]]) -> None:
        if deterministic_graph_enabled():
            edges_groups = self._stable_edge_groups(edges_groups)
        if self.frozen_vertices:
            edges_groups = [group for group in edges_groups if group[0].origin not in self.frozen_vertices]
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

    def _stable_edge_groups(self, edges_groups: list[list[Edge]]) -> list[list[Edge]]:
        graph = self.local_graph

        def key(edge: Edge) -> tuple[Any, ...]:
            return graph.stable_edge_key(edge)

        ordered = [sorted(group, key=key) for group in edges_groups]
        ordered.sort(key=lambda group: (len(graph.out_edges[group[0].dest]), key(group[0])))
        return ordered

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
