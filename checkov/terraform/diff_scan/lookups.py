"""Lookup buckets: the units of global state a vertex's edge construction reads.

Edge construction for one origin vertex resolves references through Checkov's indexes. Each index read is a "probe" of a
bucket; the edges of an origin can only change when a bucket it probed changes. A bucket changes when a vertex is added
to it, removed from it, or when a member changes a field the edge builder reads from destination vertices.

Bucket ids (JSON strings):
  ["by_module_name", <module chain>, <block type>, <name>]   vertices_by_module_dependency_by_name
  ["by_name", <block type>, <name>]                          vertices_block_name_map (module outputs, tfvars)
  ["by_module", <module chain>, <block type>]                vertices_by_module_dependency (module variables/resources)
"""
from __future__ import annotations

import json
from typing import Any, Optional

from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.graph.graph_builder.deterministic import module_chain_key
from checkov.terraform.graph_builder.graph_components.block_types import BlockType
from checkov.terraform.graph_builder.graph_components.blocks import TerraformBlock
from checkov.terraform.graph_builder.incremental_graph import _anonymise
from checkov.terraform.graph_builder.local_graph import get_vertex_as_tf_module


def _chain(module: Any, root: str) -> Any:
    return _anonymise([list(m) for m in module_chain_key(module)], root)


def by_module_name(module: Any, block_type: str, name: str, root: str) -> str:
    return json.dumps(["by_module_name", _chain(module, root), block_type, name])


def by_name(block_type: str, name: str) -> str:
    return json.dumps(["by_name", block_type, name])


def by_module(module: Any, block_type: str, root: str) -> str:
    return json.dumps(["by_module", _chain(module, root), block_type])


def buckets_from_vertex_key(key: str) -> list[str]:
    """Buckets a vertex belongs to, derived from its stable key (works for vertices that no longer exist)."""
    path, chain, block_type, name, *_ = json.loads(key)
    return [json.dumps(["by_module_name", chain, block_type, name]), json.dumps(["by_name", block_type, name]),
            json.dumps(["by_module", chain, block_type])]


def static_probes(vertex: TerraformBlock, root: str) -> list[str]:
    """Probes the edge builder makes by direct index access (not through _get_possible_vertices)."""
    if vertex.block_type == BlockType.MODULE:
        instance = get_vertex_as_tf_module(vertex)
        return [by_module(instance, BlockType.VARIABLE, root), by_module(instance, BlockType.RESOURCE, root)]
    if vertex.block_type == BlockType.TF_VARIABLE:
        return [by_name(BlockType.VARIABLE, vertex.name)]
    return []


def edge_fingerprint(vertex: TerraformBlock) -> str:
    """Fields of a DESTINATION vertex the edge builder reads (module source/version, best-match address)."""
    attributes = vertex.attributes
    return json.dumps([attributes.get("source"), attributes.get("version"),
                       attributes.get(CustomAttributes.TF_RESOURCE_ADDRESS), vertex.for_each_index], default=str)


def aliases_of(vertex: TerraformBlock) -> Optional[tuple[str, str]]:
    return (vertex.name, vertex.block_type) if "alias" in vertex.attributes else None
