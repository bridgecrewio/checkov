"""Affected-only edge schedule for incremental rendering (opt-in: CHECKOV_AFFECTED_RENDER_SCHEDULE=true).

Used only when the renderer has frozen vertices (incremental mode) in deterministic mode. It produces exactly the
edge-group evaluations the global edge loop (VariableRenderer._run_edge_loop) would perform, in the same order,
without running the loop's bookkeeping over every edge of the graph.

Why the global loop's schedule can be computed in closed form
  In deterministic mode the loop's round membership depends only on the graph topology:
    * round 0 = in-edges of the initial end vertices (out-degree 0, in-degree > 0), as a list (duplicates kept);
    * after round k, a vertex v that was an origin in round k joins `end` once all its out-edges were in some round;
    * round k+1 = (in-edges of `end`) - (round k), as a set;
    * the loop stops at the first empty round or after MAX_NUMBER_OF_LOOPS rounds (the duplicate-edge early stop is
      disabled in deterministic mode).
  Evaluation results never feed back into membership (the Terraform renderer's only write to the done map, for
  output -> output edges, adds an edge of the current round, which the loop adds right after evaluating it), so with
      settle(v) = max over v's out-edges e of first(e),  first(e) = 0 if dest(e) is an initial end vertex,
                                                         otherwise settle(dest(e)) + 1   (undefined on cycles)
  an edge into an initial end vertex is in round 0 only, and any other edge e is in rounds
  first(e), first(e) + 2, first(e) + 4, ... (the "- round k" subtraction makes it alternate).
  Inside a round the loop groups edges by f"{origin}{label}", sorts each group by the stable edge key, orders the
  groups by (out-degree of group[0].dest, stable key of group[0]) and skips groups whose origin is frozen.
  Only the relative order of the evaluated groups matters, since a skipped group has no effect.

The schedule is refused (the caller runs the global loop) when exact equivalence is not guaranteed:
  * the in/out edge maps are inconsistent or miss a vertex;
  * two different (origin, label) pairs produce the same group key string;
  * Edge equality (by its string form) differs from equality of (origin, dest, label);
  * two different edges of an evaluated group, or two evaluated groups of a round, tie on their sort key (the global
    loop then orders them by set iteration order).
"""
from __future__ import annotations

import os
from collections import Counter, deque
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable, Optional

if TYPE_CHECKING:
    from checkov.common.graph.graph_builder import Edge
    from checkov.common.graph.graph_builder.local_graph import LocalGraph

AFFECTED_SCHEDULE_ENV = "CHECKOV_AFFECTED_RENDER_SCHEDULE"
SUBGRAPH_SCHEDULE_ENV = "CHECKOV_AFFECTED_SCHEDULE_IN_SUBGRAPHS"
"""Opt-in: also use the schedule for count/for_each sub-graph renders (frozen = vertices they never read)."""
VERIFY_ENV = "CHECKOV_AFFECTED_RENDER_SCHEDULE_VERIFY"
"""Test mode: also run the global loop without evaluating anything, and fail if its trace differs."""

EdgeTuple = tuple[int, int, str]


def affected_schedule_enabled() -> bool:
    return os.getenv(AFFECTED_SCHEDULE_ENV, "false").lower() == "true"


def subgraph_schedule_enabled() -> bool:
    return affected_schedule_enabled() and os.getenv(SUBGRAPH_SCHEDULE_ENV, "false").lower() == "true"


def schedule_verification_enabled() -> bool:
    return os.getenv(VERIFY_ENV, "false").lower() == "true"


class ScheduleUnsupported(Exception):
    """Exact equivalence with the global loop cannot be guaranteed for this graph."""


@dataclass
class EdgeSchedule:
    rounds: list[list[list[Edge]]] = field(default_factory=list)
    """per executed round: the edge groups to evaluate, in evaluation order"""
    loops: int = 0
    """rounds the global loop executes"""
    reached_cap: bool = False

    def trace(self) -> list[tuple[EdgeTuple, ...]]:
        return [tuple(as_tuple(e) for e in group) for groups in self.rounds for group in groups]

    @property
    def groups(self) -> int:
        return sum(len(groups) for groups in self.rounds)

    @property
    def edges(self) -> int:
        return sum(len(group) for groups in self.rounds for group in groups)


def as_tuple(edge: Edge) -> EdgeTuple:
    return edge.origin, edge.dest, edge.label


def group_key(edge: Edge) -> str:
    """The global loop's grouping key (VariableRenderer.group_edges_by_origin_and_label)."""
    return f"{edge.origin}{edge.label}"


class _StableKeys:
    """Stable vertex keys, computed once per vertex. Rendering writes attributes only, never the fields the key reads
    (path, module chain, block type, name, for_each index)."""

    def __init__(self, graph: LocalGraph[Any]) -> None:
        self._graph = graph
        self._keys: dict[int, tuple[str, ...]] = {}

    def vertex(self, index: int) -> tuple[str, ...]:
        key = self._keys.get(index)
        if key is None:
            key = self._graph.stable_vertex_key(index)
            self._keys[index] = key
        return key

    def edge(self, edge: Edge) -> tuple[Any, ...]:
        return self.vertex(edge.origin), edge.label, self.vertex(edge.dest)


def _check_edge_maps(graph: LocalGraph[Any]) -> None:
    vertex_count = len(graph.vertices)
    for name, edge_map in (("in_edges", graph.in_edges), ("out_edges", graph.out_edges)):
        if set(edge_map.keys()) != set(range(vertex_count)):
            raise ScheduleUnsupported(f"{name} does not hold exactly one entry per vertex")
    from_out: Counter[EdgeTuple] = Counter()
    from_in: Counter[EdgeTuple] = Counter()
    for origin, edges in graph.out_edges.items():
        for edge in edges:
            if edge.origin != origin:
                raise ScheduleUnsupported("out_edges holds an edge under a different origin")
            from_out[as_tuple(edge)] += 1
    for dest, edges in graph.in_edges.items():
        for edge in edges:
            if edge.dest != dest:
                raise ScheduleUnsupported("in_edges holds an edge under a different destination")
            from_in[as_tuple(edge)] += 1
    if from_out != from_in:
        raise ScheduleUnsupported("in_edges and out_edges hold different edges")
    _check_edge_identity(from_out)


def _check_edge_identity(edges: Counter[EdgeTuple]) -> None:
    from checkov.common.graph.graph_builder import Edge

    if len({str(Edge(*edge)) for edge in edges}) != len(edges):
        raise ScheduleUnsupported("two different edges have the same string form (Edge equality)")
    pairs_by_key: dict[str, tuple[int, str]] = {}
    for origin, _, label in edges:
        pair = (origin, label)
        if pairs_by_key.setdefault(f"{origin}{label}", pair) != pair:
            raise ScheduleUnsupported(f"edge group key collision: {origin!r}/{label!r}")


def settle_rounds(graph: LocalGraph[Any], initial_end: set[int]) -> list[Optional[int]]:
    """settle(v) for every vertex (None: never settles, e.g. on a cycle or downstream of one)."""
    remaining = [len(graph.out_edges[v]) for v in range(len(graph.vertices))]
    latest = [0] * len(graph.vertices)
    settled: list[Optional[int]] = [None] * len(graph.vertices)
    queue: deque[int] = deque()

    def reach(dest: int, first: int) -> None:
        for edge in graph.in_edges[dest]:
            origin = edge.origin
            if first > latest[origin]:
                latest[origin] = first
            remaining[origin] -= 1
            if remaining[origin] == 0:
                settled[origin] = latest[origin]
                queue.append(origin)

    for dest in initial_end:
        reach(dest, 0)
    while queue:
        vertex = queue.popleft()
        reach(vertex, settled[vertex] + 1)  # type: ignore[operator]  # set before queued
    return settled


def _loop_length(graph: LocalGraph[Any], initial_end: set[int], settled: list[Optional[int]],
                 max_loops: int) -> int:
    """Number of rounds the global loop executes: up to the first empty round, at most max_loops."""
    if not initial_end:
        return 0
    first_rounds: Counter[int] = Counter()
    for dest, edges in graph.in_edges.items():
        if dest in initial_end or settled[dest] is None:
            continue
        for edge in set(edges):
            first_rounds[settled[dest] + 1] += 1  # type: ignore[operator]  # checked above
    for round_index in range(1, max_loops):
        if not any(first_rounds[s] for s in range(round_index % 2 or 2, round_index + 1, 2)):
            return round_index
    return max_loops


def initial_end_vertices(graph: LocalGraph[Any]) -> set[int]:
    """VariableRenderer._get_initial_end_vertices: out-degree 0 and in-degree > 0."""
    return {v for v, edges in graph.out_edges.items() if not edges and graph.in_edges.get(v)}


def edge_loop_rounds(graph: LocalGraph[Any], max_loops: int) -> int:
    """Rounds the global edge loop executes on this graph (deterministic mode). A pure function of the topology."""
    initial_end = initial_end_vertices(graph)
    return _loop_length(graph, initial_end, settle_rounds(graph, initial_end), max_loops)


def _round_edges(graph: LocalGraph[Any], evaluated_origins: list[int], initial_end: set[int],
                 settled: list[Optional[int]], loops: int) -> list[list[Edge]]:
    rounds: list[list[Edge]] = [[] for _ in range(loops)]
    if not loops:
        return rounds
    for origin in evaluated_origins:
        for edge in graph.out_edges[origin]:
            dest = edge.dest
            if dest in initial_end:
                rounds[0].append(edge)
                continue
            if settled[dest] is None:
                continue
            for round_index in range(settled[dest] + 1, loops, 2):  # type: ignore[operator]  # checked above
                rounds[round_index].append(edge)
    for round_index in range(1, loops):
        rounds[round_index] = list({as_tuple(e): e for e in rounds[round_index]}.values())
    return rounds


def _ordered_groups(graph: LocalGraph[Any], edges: list[Edge], keys: _StableKeys) -> list[list[Edge]]:
    def edge_order(edge: Edge) -> tuple[Any, ...]:
        return len(graph.out_edges[edge.dest]), keys.edge(edge)

    groups: dict[str, list[Edge]] = {}
    for edge in edges:
        groups.setdefault(group_key(edge), []).append(edge)
    ordered = [sorted(group, key=keys.edge) for group in groups.values()]
    for group in ordered:
        _reject_ties(group, keys.edge, "edges of one group")
    ordered.sort(key=lambda group: edge_order(group[0]))
    _reject_ties([group[0] for group in ordered], edge_order, "edge groups of one round")
    return ordered


def _reject_ties(edges: list[Edge], key: Callable[[Edge], Any], what: str) -> None:
    for previous, current in zip(edges, edges[1:]):
        if as_tuple(previous) != as_tuple(current) and key(previous) == key(current):
            raise ScheduleUnsupported(f"sort-key tie between {what}: {as_tuple(previous)} / {as_tuple(current)}")


def build_affected_schedule(graph: LocalGraph[Any], frozen: set[int], initial_end: set[int],
                            max_loops: int) -> EdgeSchedule:
    """The evaluations the global edge loop performs when every edge group with a frozen origin is skipped.
    Raises ScheduleUnsupported when exact equivalence cannot be guaranteed."""
    _check_edge_maps(graph)
    control = os.getenv(NEGATIVE_CONTROL_ENV, "")
    if control == "schedule_no_cap":
        max_loops = 10 * len(graph.vertices) + 2
    settled = settle_rounds(graph, initial_end)
    loops = _loop_length(graph, initial_end, settled, max_loops)
    evaluated_origins = [v for v in range(len(graph.vertices)) if v not in frozen and graph.out_edges[v]]
    keys = _StableKeys(graph)
    round_edges = _round_edges(graph, evaluated_origins, initial_end, settled, loops)
    if control == "schedule_skip_frozen_dest":
        round_edges = [[e for e in edges if e.dest not in frozen] for edges in round_edges]
    rounds = [_ordered_groups(graph, edges, keys) for edges in round_edges]
    return _weakened(EdgeSchedule(rounds=rounds, loops=loops, reached_cap=loops >= max_loops), control)


NEGATIVE_CONTROL_ENV = "DFO_NEGATIVE"
"""PoC test hook: deliberately wrong schedules, to show what the correctness suite can and cannot observe."""


def _weakened(schedule: EdgeSchedule, control: str) -> EdgeSchedule:
    if control == "schedule_single_pass":
        seen: set[EdgeTuple] = set()
        rounds = []
        for groups in schedule.rounds:
            fresh = [g for g in groups if as_tuple(g[0]) not in seen]
            seen.update(as_tuple(g[0]) for g in fresh)
            rounds.append(fresh)
        schedule.rounds = rounds
    elif control == "schedule_reversed_rounds":
        schedule.rounds = [list(reversed(groups)) for groups in schedule.rounds]
    return schedule
