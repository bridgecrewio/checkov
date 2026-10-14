"""Deterministic graph evaluation mode (opt-in).

Enabled with the environment variable CHECKOV_DETERMINISTIC_GRAPH=true (or the CLI flag
--deterministic-graph). When OFF, Checkov behaves exactly as upstream.

Why it exists: upstream variable rendering evaluates edges in an order derived from vertex indices,
and substitutes references one at a time, re-evaluating the half-substituted expression after each
step. For expressions such as "${var.a && var.b}" the order changes the result, and vertex indices
depend on everything else parsed in the same run. A finding for resource X can therefore change when
an unrelated directory is added to the repository. Incremental (PR diff) scanning needs the opposite
guarantee: evaluating a sub-graph must give the same result as evaluating it inside the full graph.

Deterministic mode:
  * orders edges by a stable identity of their endpoints (file, module chain, block type, name)
  * disables the renderer's graph-wide "too many duplicate edges" early stop, which made one
    component's rendering depend on the size of unrelated components
  * includes the module call chain in graph-check and record identities, so instances of the same
    module called from different root modules are not merged
  * Terraform edges stay inside one module instance: a module output reference connects only to the
    instance created by that module block, and a counted / for_each block's `virtual_resource` edges
    connect only to its own expanded instances (upstream matches both by name / caller file, which links
    root modules that reach the same module code)
  * a record's breadcrumbs come from its own module instance (upstream keys them by file + address, so the
    last root module calling the same module code wins)
  * `toset()` values and for_each expansion follow a sorted order (upstream follows the per-process hash seed)
"""
from __future__ import annotations

import os
from typing import Any

DETERMINISTIC_GRAPH_ENV = "CHECKOV_DETERMINISTIC_GRAPH"
INCREMENTAL_GRAPH_ENV = "CHECKOV_INCREMENTAL_GRAPH"


def deterministic_graph_enabled() -> bool:
    return os.getenv(DETERMINISTIC_GRAPH_ENV, "false").lower() == "true"


ISOLATE_CHECK_CONFIG_ENV = "CHECKOV_ISOLATE_CHECK_CONFIG"


def isolate_check_config_enabled() -> bool:
    """Opt-in: Python resource checks get a private copy of the entity config.

    Upstream BaseResourceCheck.scan_entity_conf() runs handle_dynamic_values(conf), which APPENDS dynamic-block content
    to conf; for Terraform conf is the graph vertex's own config, so every check that runs grows the vertex (and the
    graph handed to graph checks and to callers). With this flag the graph is left exactly as rendering produced it.
    Each check still sees what upstream's FIRST check sees (one expansion), so results can differ from upstream only
    where a later check relied on an already-duplicated block list."""
    return os.getenv(ISOLATE_CHECK_CONFIG_ENV, "false").lower() == "true"


def incremental_graph_enabled() -> bool:
    """Opt-in on top of deterministic mode: a vertex's rendered state depends only on the vertices it references.

    Upstream hands the referenced vertex's own breadcrumb list to the referencing vertex and appends to it, so a
    vertex's breadcrumbs grow with every block that references it. Incremental rendering reuses vertices whose
    references did not change, which is only exact when nothing upstream can write into them."""
    return deterministic_graph_enabled() and os.getenv(INCREMENTAL_GRAPH_ENV, "false").lower() == "true"


REALPATH_MEMO_ENV = "CHECKOV_REALPATH_MEMO"


def realpath_memo_enabled() -> bool:
    """Opt-in (set by the diff-files-only scan): Terraform edge lookups memoise os.path.realpath of the referencing
    vertex's path, as they already do for the referenced vertices' paths. Same values; the file system is not changed
    while a graph is built."""
    return os.getenv(REALPATH_MEMO_ENV, "false").lower() == "true"


STABLE_KEY_CACHE_ENV = "CHECKOV_STABLE_KEY_CACHE"


def stable_key_cache_enabled() -> bool:
    """Opt-in (set by the diff-files-only scan): the global edge loop computes each vertex's stable key once per loop
    instead of on every sort comparison. Same keys, same order."""
    return os.getenv(STABLE_KEY_CACHE_ENV, "false").lower() == "true"


def module_chain_key(module: Any) -> tuple[tuple[str, str, str], ...]:
    """Terraform TFModule chain (outer -> inner) as a tuple. Empty for every other framework."""
    chain: list[tuple[str, str, str]] = []
    while module is not None:
        chain.append((str(getattr(module, "path", "")), str(getattr(module, "name", "")),
                      str(getattr(module, "foreach_idx", ""))))
        module = getattr(module, "nested_tf_module", None)
    return tuple(reversed(chain))


def stable_block_key(block: Any) -> tuple[str, ...]:
    return (
        str(getattr(block, "path", "")),
        str(module_chain_key(getattr(block, "source_module_object", None))),
        str(getattr(block, "block_type", "")),
        str(getattr(block, "name", "")),
        str(getattr(block, "for_each_index", "")),
    )
