"""Root-module units: the granularity at which count/for_each expansion is scoped.

A unit is one root directory D plus every module instance loaded from it:
  * definition keys with no module chain whose file is in D
  * definition keys whose OUTERMOST chain entry (the root module call) is in a file in D
  * tfvar vertices loaded for D (`load_dir` == D)

Within a unit Checkov's pre-render pipeline never reads another unit's vertices, except through the global token
lists `aliases` and `resources_types` (checked separately): reference lookups are keyed by module chain + same
directory, module output / variable lookups by the calling module instance, virtual-resource edges by same instance.
So a unit can be built on its own with Checkov's own build_pre_render_graph(), count/for_each expansion included.
"""
from __future__ import annotations

import os
from typing import Any, Optional

from checkov.common.util.data_structures_utils import pickle_deepcopy
from checkov.terraform.graph_builder.graph_components.block_types import BlockType
from checkov.terraform.graph_builder.graph_components.module import Module
from checkov.terraform.graph_builder.local_graph import TerraformLocalGraph
from checkov.terraform.modules.module_objects import TFDefinitionKey

from checkov.terraform.diff_scan.recorder import EdgeRecorder


def outermost_module(module: Any) -> Any:
    while module is not None and module.nested_tf_module is not None:
        module = module.nested_tf_module
    return module


def unit_of_key(key: TFDefinitionKey) -> str:
    root = outermost_module(key.tf_source_modules)
    return os.path.dirname(root.path if root is not None else key.file_path)


def unit_of_vertex(vertex: Any) -> str:
    if vertex.block_type == BlockType.TF_VARIABLE:
        return str(vertex.attributes.get("load_dir"))
    root = outermost_module(vertex.source_module_object)
    return os.path.dirname(root.path if root is not None else vertex.path)


def has_count_or_foreach(definition: dict[str, Any]) -> bool:
    """Same test as TerraformLocalGraph._create_vertices: a module/resource/data block with count or for_each."""
    for block_type in (BlockType.RESOURCE, BlockType.MODULE, BlockType.DATA):
        for block in definition.get(block_type, []):
            if not isinstance(block, dict):
                continue
            for value in block.values():
                configs = [value] if block_type == BlockType.MODULE else list(value.values()) \
                    if isinstance(value, dict) else []
                if any(isinstance(c, dict) and ("count" in c or "for_each" in c) for c in configs):
                    return True
    return False


def build_unit(definitions: dict[TFDefinitionKey, Any], tfvar_blocks: list[Any], module_fields: dict[str, Any],
               root: str, global_resource_types: Optional[set[str]] = None,
               global_aliases: Optional[dict[str, dict[str, str]]] = None,
               statement_oracle: Optional[Any] = None) -> tuple[TerraformLocalGraph, EdgeRecorder]:
    """Checkov's own pre-render pipeline (count/for_each expansion included) on one unit's definitions only.
    `tfvar_blocks`: the unit's tfvar blocks as Module.add_blocks creates them (pre-pipeline).
    `global_resource_types` / `global_aliases`: Checkov's lookup lists as they are for the WHOLE PR graph (a full build
    resolves `aws_x.name` against every unit's resource types and aliases, not just this unit's).
    `statement_oracle`: expansions.ExpansionOracle; count / for_each statements whose read closure is unchanged since
    the baseline are reused instead of re-rendered."""
    module = Module(source_dir=module_fields["source_dir"],
                    external_modules_source_map=module_fields["external_modules_source_map"])
    module.source = module_fields["source"]
    module.blocks.extend(pickle_deepcopy(tfvar_blocks))
    module.temp_tf_definition = definitions
    copies = pickle_deepcopy(definitions)
    for key in sorted(copies):
        for block_type in copies[key]:
            module.add_blocks(block_type, copies[key][block_type], key, module.source)
    if global_resource_types is not None:
        module.resources_types = set(module.resources_types) | set(global_resource_types)
    graph = TerraformLocalGraph(module)
    if statement_oracle is not None:
        graph.foreach_statement_oracle = statement_oracle
    if global_aliases is not None:
        local_aliases = graph._get_aliases
        graph._get_aliases = lambda: {**global_aliases, **local_aliases()}  # type: ignore[method-assign]
    recorder = EdgeRecorder(graph, root)
    recorder.install()
    try:
        graph.build_pre_render_graph()
    finally:
        recorder.uninstall()
    return graph, recorder


def pre_expansion_unit_graph(definitions: dict[TFDefinitionKey, Any], tfvar_blocks: list[Any],
                             module_fields: dict[str, Any], global_resource_types: set[str],
                             global_aliases: dict[str, dict[str, str]]) -> TerraformLocalGraph:
    """The unit's graph exactly as Checkov's build_pre_render_graph() leaves it right BEFORE the count / for_each
    handler runs: vertices created, one _build_edges pass. This is the graph the handler decides statements on."""
    module = Module(source_dir=module_fields["source_dir"],
                    external_modules_source_map=module_fields["external_modules_source_map"])
    module.source = module_fields["source"]
    module.blocks.extend(pickle_deepcopy(tfvar_blocks))
    module.temp_tf_definition = definitions
    copies = pickle_deepcopy(definitions)
    for key in sorted(copies):
        for block_type in copies[key]:
            module.add_blocks(block_type, copies[key][block_type], key, module.source)
    module.resources_types = set(module.resources_types) | set(global_resource_types)
    graph = TerraformLocalGraph(module)
    local_aliases = graph._get_aliases
    graph._get_aliases = lambda: {**global_aliases, **local_aliases()}  # type: ignore[method-assign]
    graph._create_vertices()
    graph._build_edges()
    return graph
