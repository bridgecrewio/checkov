"""Baseline artifact (v2) for diff-files-only PR scans.

Everything a PR scan needs that a full build would otherwise derive from unchanged repository files:

  vertices       the pre-render graph's vertices exactly as build_pre_render_graph() left them, in Checkov's vertex
                 order, one pickle per vertex (only the vertices a PR reuses are ever unpickled)
  keys           stable vertex key per vertex (incremental_graph.vertex_key)
  edges          pre-render edges [origin, dest, label, owner, phase] by vertex index
  probes         index buckets each edge owner read while building its edges (lookups.py)
  aliases        provider aliases the edge builder used ({name: block type})
  definitions    parsed + cleaned definitions per TFDefinitionKey (pickled; as handed to Module.add_blocks)
  resource_types resource types contributed by each definition key (Module.resources_types is their union)
  files          every repository file the runner reads after the graph is built: path -> lines
  module         Module fields the post-render passes read (source, external_modules_source_map, source_dir)
  foreach_ran    whether count/for_each expansion ran in the baseline build
  rendered       the resource-level artifact (incremental_graph.export_graph) of the same build

The PR scan runs at the same absolute root as the baseline (the harness guarantees it), so pickled blocks are used as-is.
"""
from __future__ import annotations

import base64
import pickle
from typing import Any

ARTIFACT_VERSION = 2


def dumps(value: Any) -> str:
    return base64.b64encode(pickle.dumps(value)).decode()


def loads(text: str | bytes) -> Any:
    """A base64 pickle (v2 JSON artifact) or raw pickle bytes (v3 section store, artifact_store.PickledItem)."""
    data = text if isinstance(text, bytes) else base64.b64decode(text)
    return pickle.loads(data)  # noqa: S301  # written by our own baseline scan
