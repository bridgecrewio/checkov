"""Baseline capture: the pre-render part of the v2 artifact, taken around build_pre_render_graph()."""
from __future__ import annotations

import hashlib
import json
import os
from collections import defaultdict
from typing import Any

from checkov.common.graph.graph_builder.deterministic import module_chain_key
from checkov.common.util.json_utils import CustomJSONEncoder
from checkov.terraform.graph_builder.graph_components.block_types import BlockType
from checkov.terraform.graph_builder.incremental_graph import vertex_keys
from checkov.terraform.graph_builder.local_graph import TerraformLocalGraph
from checkov.terraform.modules.module_objects import TFDefinitionKey

from checkov.terraform.diff_scan import lookups
from checkov.terraform.diff_scan.artifact import ARTIFACT_VERSION, dumps
from checkov.terraform.diff_scan.recorder import EdgeRecorder
from checkov.terraform.diff_scan.units import has_count_or_foreach, unit_of_key, unit_of_vertex


def definition_key_of(vertex: Any) -> TFDefinitionKey:
    return TFDefinitionKey(file_path=vertex.path, tf_source_modules=vertex.source_module_object)


def resource_types_of(definition: dict[str, Any]) -> list[str]:
    return sorted({resource_type for block in definition.get(BlockType.RESOURCE, []) for resource_type in block})


def creation_digest(block: Any, root: str) -> str:
    """Identity of a block as Module.add_blocks creates it, before any graph pass touches it. Root-relative (the
    root is anonymised), so it is stable when the artifact is relocated."""
    payload = [block.name, block.block_type, block.path, [list(m) for m in module_chain_key(block.source_module_object)],
               block.attributes, block.config, block.id, block.source, block.has_dynamic_block,
               getattr(block, "dynamic_attributes", None), getattr(block, "foreach_attrs", None),
               block.for_each_index]
    text = json.dumps(payload, cls=CustomJSONEncoder, sort_keys=True, default=str).replace(root, "<root>")
    return hashlib.sha256(text.encode()).hexdigest()


def aliases_signature(graph: TerraformLocalGraph) -> list[list[str]]:
    return sorted([name, str(info.get("block_type_"))] for name, info in graph._get_aliases().items())


def _alias_keys(graph: TerraformLocalGraph) -> dict[str, list[str]]:
    """alias name -> definition keys of the vertices that carry it (an alias stays global while any survives)."""
    keys: dict[str, list[str]] = defaultdict(list)
    for vertex in graph.vertices:
        if "alias" in vertex.attributes and vertex.block_type != BlockType.TF_VARIABLE:
            keys[vertex.name].append(dumps(definition_key_of(vertex)))
    return dict(keys)


def tf_var_environment() -> dict[str, str]:
    return {k: v for k, v in sorted(os.environ.items()) if k.startswith("TF_VAR_")}


def _vertices_by_definition(graph: TerraformLocalGraph) -> tuple[list[int], dict[TFDefinitionKey, list[int]]]:
    tfvars: list[int] = []
    by_definition: dict[TFDefinitionKey, list[int]] = defaultdict(list)
    for index, vertex in enumerate(graph.vertices):
        if vertex.block_type == BlockType.TF_VARIABLE:
            tfvars.append(index)
        else:
            by_definition[definition_key_of(vertex)].append(index)
    return tfvars, by_definition


def _read_lines(path: str) -> list[str]:
    with open(path, "r") as f:
        return f.readlines()


def _tfvar_unit(graph: TerraformLocalGraph, index: int, unit_by_vertex: list[str]) -> str:
    """A tfvar vertex belongs to the unit of the variable it feeds (Checkov connects it to the FIRST variable of that
    name in its load_dir, whatever unit that variable is in); unconnected tfvars keep their load_dir."""
    feeders = [unit_by_vertex[e.origin] for e in graph.in_edges.get(index, [])]
    return feeders[0] if feeders else unit_by_vertex[index]


def _cross_unit_links(graph: TerraformLocalGraph, owners: list[Any], unit_by_vertex: list[str]) -> list[str]:
    """Edges, edge owners, source_module and module_connections links that leave a vertex's unit."""
    crossing = []
    for edge, (owner, _) in zip(graph.edges, owners):
        if len({unit_by_vertex[edge.origin], unit_by_vertex[edge.dest], unit_by_vertex[owner]}) > 1:
            crossing.append(f"edge {graph.vertices[edge.origin].name} -> {graph.vertices[edge.dest].name}")
    for index, vertex in enumerate(graph.vertices):
        linked = set(vertex.source_module) | {i for ids in vertex.module_connections.values() for i in ids}
        crossing += [f"index link {vertex.name} -> {graph.vertices[i].name}" for i in linked
                     if unit_by_vertex[i] != unit_by_vertex[index]]
    return crossing


def _unit_info(definitions: dict[TFDefinitionKey, Any], unit_by_vertex: list[str]) -> dict[str, Any]:
    info: dict[str, Any] = defaultdict(lambda: {"has_foreach": False, "vertices": []})
    for key, definition in definitions.items():
        unit = info[unit_of_key(key)]
        unit["has_foreach"] = unit["has_foreach"] or has_count_or_foreach(definition)
    for index, unit in enumerate(unit_by_vertex):
        info[unit]["vertices"].append(index)
    return dict(info)


def capture_pre_render(graph: TerraformLocalGraph, recorder: EdgeRecorder, creation_digests: list[str],
                       root: str) -> dict[str, Any]:
    definitions = graph.module.temp_tf_definition
    definition_keys = sorted(definitions)
    tfvars, by_definition = _vertices_by_definition(graph)
    expected_order = tfvars + [i for key in definition_keys for i in by_definition.get(key, [])]
    owners = recorder.final_edge_owners()
    unit_by_vertex = [unit_of_vertex(v) for v in graph.vertices]
    for index, vertex in enumerate(graph.vertices):
        if vertex.block_type == BlockType.TF_VARIABLE:
            unit_by_vertex[index] = _tfvar_unit(graph, index, unit_by_vertex)
    crossing = _cross_unit_links(graph, owners, unit_by_vertex)
    return {
        "version": ARTIFACT_VERSION,
        "root": root,
        "foreach_ran": any(graph.foreach_blocks.values()),
        "order_matches_definitions": expected_order == list(range(len(graph.vertices))),
        "unit_by_vertex": unit_by_vertex,
        "units": _unit_info(definitions, unit_by_vertex),
        "units_isolated": not crossing,
        "cross_unit_links": crossing[:20],
        "source_module": [sorted(v.source_module) for v in graph.vertices],
        "module_connections": [{k: list(ids) for k, ids in v.module_connections.items()} for v in graph.vertices],
        "tf_var_environment": tf_var_environment(),
        "keys": vertex_keys(graph, root),
        "vertices": [dumps(v) for v in graph.vertices],
        "creation_digests": creation_digests,
        "fingerprints": [lookups.edge_fingerprint(v) for v in graph.vertices],
        "tfvar_vertices": tfvars,
        "edges": [[e.origin, e.dest, e.label, owner, phase] for e, (owner, phase) in zip(graph.edges, owners)],
        "probes": {str(i): sorted(p) for i, p in recorder.probes.items()},
        "aliases": aliases_signature(graph),
        "alias_keys": _alias_keys(graph),
        "definitions": [{"key": dumps(key), "definition": dumps(definitions[key]),
                         "resource_types": resource_types_of(definitions[key]),
                         "vertices": by_definition.get(key, [])} for key in definition_keys],
        "files": {path: _read_lines(path) for path in sorted({key.file_path for key in definition_keys})},
        "module": dumps({"source": graph.module.source, "source_dir": graph.module.source_dir,
                         "external_modules_source_map": graph.module.external_modules_source_map}),
    }
