"""Instrumentation of TerraformLocalGraph edge construction.

Records, for every pre-render edge, the vertex whose edge-building call created it (its "owner") and the build phase:
  build     _build_edges_for_vertex + _build_virtual_resources_edges (one loop iteration of _build_edges)
  provider  _connect_module_provider_for_vertex
and every index bucket each owner read while building its edges (see lookups.py). A PR scan reuses an owner's edges
verbatim unless the owner changed or one of the buckets it read changed.

When for_each/count expansion runs, Checkov discards every edge (_arrange_graph_data) and builds them all again; the
recorder resets with it, so what it holds at the end describes exactly the final edge list.
"""
from __future__ import annotations

import json
from collections import defaultdict
from typing import Any, Callable, Optional

from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.util.consts import RESOLVED_MODULE_ENTRY_NAME
from checkov.terraform.graph_builder.graph_components.block_types import BlockType
from checkov.terraform.graph_builder.local_graph import TerraformLocalGraph
from checkov.terraform.modules.module_objects import TFDefinitionKey

from checkov.terraform.diff_scan import lookups

BUILD_PHASE = "build"
PROVIDER_PHASE = "provider"
_WRAPPED = ("_build_edges_for_vertex", "_build_virtual_resources_edges", "_connect_module_provider_for_vertex",
            "_get_possible_vertices", "_connect_module", "create_edge", "_arrange_graph_data")


class EdgeRecorder:
    def __init__(self, graph: TerraformLocalGraph, root: str) -> None:
        self.graph = graph
        self.root = root
        self.owner: Optional[int] = None
        self.phase: Optional[str] = None
        self.edge_owners: list[tuple[Optional[int], Optional[str]]] = []
        self.probes: dict[int, set[str]] = defaultdict(set)

    def install(self) -> None:
        graph = self.graph
        graph._build_edges_for_vertex = self._owned(graph._build_edges_for_vertex, BUILD_PHASE, self._static_probes)
        graph._build_virtual_resources_edges = self._owned(graph._build_virtual_resources_edges, BUILD_PHASE,
                                                           self._virtual_probes)
        graph._connect_module_provider_for_vertex = self._owned(graph._connect_module_provider_for_vertex,
                                                                PROVIDER_PHASE, self._provider_probes)
        graph._get_possible_vertices = self._probing_possible_vertices(graph._get_possible_vertices)
        graph._connect_module = self._probing_connect_module(graph._connect_module)
        graph.create_edge = self._recording_create_edge(graph.create_edge)
        graph._arrange_graph_data = self._resetting(graph._arrange_graph_data)

    def uninstall(self) -> None:
        for name in _WRAPPED:
            vars(self.graph).pop(name, None)

    def final_edge_owners(self) -> list[tuple[Optional[int], Optional[str]]]:
        if len(self.edge_owners) != len(self.graph.edges):
            raise RuntimeError("edge recorder out of sync with the graph's edge list")
        if any(owner is None for owner, _ in self.edge_owners):
            raise RuntimeError("pre-render edge created outside an owned edge-building call")
        return self.edge_owners

    def _owned(self, method: Callable[..., Any], phase: str,
               probes: Callable[[int], list[str]]) -> Callable[..., Any]:
        def wrapper(origin_node_index: int, *args: Any, **kwargs: Any) -> Any:
            self.owner, self.phase = origin_node_index, phase
            self.probes[origin_node_index].update(probes(origin_node_index))
            try:
                return method(origin_node_index, *args, **kwargs)
            finally:
                self.owner, self.phase = None, None

        return wrapper

    def _static_probes(self, index: int) -> list[str]:
        return lookups.static_probes(self.graph.vertices[index], self.root)

    def _virtual_probes(self, index: int) -> list[str]:
        vertex = self.graph.vertices[index]
        names = vertex.config.get(CustomAttributes.VIRTUAL_RESOURCES) or []
        return [lookups.by_module_name(vertex.source_module_object, vertex.block_type, name, self.root)
                for name in names]

    def _provider_probes(self, index: int) -> list[str]:
        vertex = self.graph.vertices[index]
        if vertex.block_type != BlockType.MODULE:
            return []
        resolved = vertex.config.get(vertex.name, {}).get(RESOLVED_MODULE_ENTRY_NAME)
        if not resolved or not isinstance(resolved, list):
            return []
        first = resolved[0]
        key = TFDefinitionKey.from_json(json.loads(first)) if isinstance(first, str) else first
        return [lookups.by_module(key.tf_source_modules, BlockType.RESOURCE, self.root)]

    def _probing_possible_vertices(self, method: Callable[..., list[int]]) -> Callable[..., list[int]]:
        def wrapper(module_key: Any, block_type: str, name: str) -> list[int]:
            if self.owner is not None:
                normalised = name.replace('["', "[").replace('"]', "]")
                for candidate in {name, normalised}:
                    self.probes[self.owner].add(lookups.by_module_name(module_key, block_type, candidate, self.root))
            return method(module_key, block_type, name)

        return wrapper

    def _probing_connect_module(self, method: Callable[..., None]) -> Callable[..., None]:
        def wrapper(sub_values: list[str], *args: Any, **kwargs: Any) -> None:
            if self.owner is not None and len(sub_values) > 1:
                self.probes[self.owner].add(lookups.by_name(BlockType.OUTPUT, sub_values[1]))
            return method(sub_values, *args, **kwargs)

        return wrapper

    def _recording_create_edge(self, method: Callable[..., bool]) -> Callable[..., bool]:
        def wrapper(*args: Any, **kwargs: Any) -> bool:
            created = method(*args, **kwargs)
            if created:
                self.edge_owners.append((self.owner, self.phase))
            return created

        return wrapper

    def _resetting(self, method: Callable[[], None]) -> Callable[[], None]:
        def wrapper() -> None:
            self.edge_owners = []
            self.probes = defaultdict(set)
            method()

        return wrapper
