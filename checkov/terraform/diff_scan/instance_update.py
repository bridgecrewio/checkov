"""Instance-level count / for_each update of one unit (Round 8): the unit's expanded pre-render vertex list without
running Checkov's whole pre-render pipeline.

Checkov's resource / data expansion (ForeachEntityHandler) is a pure function of the pre-expansion block and its
statement (expansion value): instance i is pickle_deepcopy(main block) with count.index / each.key / each.value
substituted, renamed `name[i]` / `name["k"]`; with RAW_TF_IN_GRAPH the main block stays, with `virtual_resources`
listing its instances. So for every counted / for_each resource or data block of the unit:

  creation state unchanged (creation digest)  AND  statement unchanged (expansions.ExpansionOracle)
      -> its baseline vertices (main block + instances) are reused as they are
  otherwise
      -> its vertices are recreated with Checkov's own instance code (_create_new_resource on a scratch graph);
         a recreated vertex identical to the baseline's (creation digest) is swapped back to the baseline vertex

Blocks without count / for_each follow the usual per-owner rule (reuse when the creation digest is unchanged).
The resulting vertex list goes through the per-owner edge engine (edges rebuilt only for owners that are new /
changed or read a lookup bucket that changed: added / removed instances change the buckets of `aws_x.name[i]`).

Exactness conditions (else IncrementalGraphUnsupported -> caller falls back to the unit rebuild):
  * no module block with count / for_each in the unit (module expansion copies whole subtrees and rewrites the
    module chains of every child: not reproduced here)
  * the baseline's vertex order for the unit is Checkov's order (artifact `order_matches_definitions` is not needed:
    order is restored per definition key, and rendering / edges are order-independent, verified by the suites)
  * every statement could be determined (static or via the oracle)
"""
from __future__ import annotations

import os
from typing import Any, Optional

from checkov.common.util.data_structures_utils import pickle_deepcopy
from checkov.terraform.diff_scan.artifact import loads
from checkov.common.util.env_vars_config import env_vars_config
from checkov.terraform.graph_builder.foreach.consts import COUNT_STRING, FOREACH_STRING
from checkov.terraform.graph_builder.graph_components.block_types import BlockType
from checkov.terraform.graph_builder.incremental_graph import IncrementalGraphUnsupported

NEGATIVE_CONTROL = os.getenv("DFO_NEGATIVE", "")
INSTANCE_UPDATE_ENV = "CHECKOV_DIFF_INSTANCE_LEVEL_FOREACH"


def instance_update_enabled() -> bool:
    return os.getenv(INSTANCE_UPDATE_ENV, "false").lower() == "true"


def is_counted(block: Any) -> bool:
    return block.block_type in (BlockType.RESOURCE, BlockType.DATA, BlockType.MODULE) and (
        FOREACH_STRING in block.attributes or COUNT_STRING in block.attributes)


def is_expanded(block: Any) -> bool:
    """Whether Checkov's pre-render build expands this block (TerraformLocalGraph enable_* switches, same env vars
    and defaults: resources yes, data blocks only with CHECKOV_ENABLE_DATAS_FOREACH_HANDLING)."""
    from checkov.common.runners.base_runner import strtobool

    if not is_counted(block):
        return False
    if block.block_type == BlockType.RESOURCE:
        return bool(strtobool(os.getenv("CHECKOV_ENABLE_FOREACH_HANDLING", "True")))
    if block.block_type == BlockType.DATA:
        return bool(strtobool(os.getenv("CHECKOV_ENABLE_FOREACH_HANDLING", "True"))) and \
            bool(strtobool(os.getenv("CHECKOV_ENABLE_DATAS_FOREACH_HANDLING", "False")))
    return bool(strtobool(os.getenv("CHECKOV_ENABLE_MODULES_FOREACH_HANDLING", "True")))


def base_name(name: str) -> str:
    return name.split("[", 1)[0]


class ScratchGraph:
    """The minimum of TerraformLocalGraph Checkov's ForeachEntityHandler instance code touches: a vertex list."""

    def __init__(self, module: Any) -> None:
        self.module = module
        self.vertices: list[Any] = []


def expand_block(block: Any, statement: Any) -> list[Any]:
    """Checkov's own expansion of one resource / data block: [instances..., main block] as a full build leaves them
    (instance 0 replaces the main block in place, the others are appended, then the main block is appended last)."""
    from checkov.terraform.graph_builder.foreach.foreach_entity_handler import ForeachEntityHandler

    scratch = ScratchGraph(None)
    scratch.vertices = [block]
    handler = ForeachEntityHandler(scratch, block.block_type)  # type: ignore[arg-type]
    if not statement:
        return [block]
    if isinstance(statement, int):
        handler._create_new_resources_count(statement, 0)
    else:
        handler._create_new_resources_foreach(statement, 0)
    return list(scratch.vertices)


def instance_names(block: Any, statement: Any) -> list[str]:
    """Names of the instances Checkov creates for this statement (count -> name[i]; for_each -> name["k"])."""
    if not statement:
        return []
    if isinstance(statement, int):
        return [f"{block.name}[{i}]" for i in range(statement)]
    keys = statement if isinstance(statement, list) else list(statement.keys())
    return [f'{block.name}["{k}"]' if isinstance(k, str) else f"{block.name}[{k}]" for k in keys]


def raw_tf_in_graph() -> bool:
    return bool(env_vars_config.RAW_TF_IN_GRAPH_ENV)


class InstanceSplicer:
    """Builds a unit's expanded pre-render vertex list from the baseline (unit sub-artifact) + the PR's definitions.

    `engine` is the unit's DiffEngine (sub-artifact: indices are unit positions). Per definition key, in sorted key
    order (Checkov's add order), each block created by Module.add_blocks is either reused from the baseline (its
    vertices: main block + instances) or (re)expanded. Returns (vertices, fresh positions, stats)."""

    def __init__(self, engine: Any, oracle: Any) -> None:
        self.e = engine
        self.oracle = oracle
        self.by_block: dict[str, list[int]] = {}
        """baseline: block key (no index) -> unit positions of its vertices (main block + instances), baseline order"""
        for position, key in enumerate(engine.old_keys):
            self.by_block.setdefault(_block_key_of_vertex_key(key), []).append(position)
        self.stats = {"blocks_reused": 0, "blocks_reexpanded": 0, "instances_created": 0, "instances_reused": 0}

    def _pre_expansion_digest(self, block: Any) -> str:
        """Creation digest of a counted MAIN block without what expansion and the encryption pass add to it
        (`virtual_resources` in its config, the encryption attributes): the baseline's stored main vertex is post-
        expansion, a freshly created block is pre-expansion; both reduce to the same state when the source block is
        unchanged."""
        from checkov.common.graph.graph_builder.graph_components.attribute_names import CustomAttributes
        from checkov.terraform.diff_scan.baseline import creation_digest

        probe = pickle_deepcopy(block)
        if isinstance(probe.config, dict):
            probe.config.pop(CustomAttributes.VIRTUAL_RESOURCES, None)
        probe.attributes.pop(CustomAttributes.ENCRYPTION, None)
        probe.attributes.pop(CustomAttributes.ENCRYPTION_DETAILS, None)
        return creation_digest(probe, self.e.root)

    def _key_has_changed_statement(self, key: Any) -> bool:
        """Whether a counted block created from this definition key has a statement differing from the baseline."""
        if NEGATIVE_CONTROL == "unchanged_key_stale_instances":
            return False
        from checkov.terraform.diff_scan.expansions import block_key

        for position in self.e.definition_entries[key]["vertices"]:
            vertex = self.e._reused_vertex(position)
            if is_expanded(vertex) and "[" not in vertex.name and \
                    self.oracle.statement_changed(block_key(vertex, self.e.root)):
                return True
        return False

    def vertices(self, parsed: dict[Any, Any], changed: set[Any], removed: set[Any],
                 module_fields: dict[str, Any]) -> tuple[list[Any], set[int]]:
        e = self.e
        self.module_fields = module_fields
        fresh: set[int] = set()
        replacement = getattr(e, "unit_tfvar_blocks", None)
        if replacement is None:
            vertices = [e._reused_vertex(i) for i in e.a["tfvar_vertices"]]
        else:
            vertices = []
            for block in replacement:
                vertices.append(e._reuse_if_unchanged(pickle_deepcopy(block), fresh, len(vertices)))
        main_blocks: list[Any] = []
        """counted main blocks are appended after every instance of the unit (RAW_TF_IN_GRAPH: Checkov appends each
        main block at the end of the vertex list); kept in expansion order"""
        for key in sorted((set(e.pickled_definitions) - removed) | changed):
            if key in changed:
                blocks = e._create_blocks(key, parsed[key], module_fields["source"],
                                          module_fields["external_modules_source_map"], module_fields["source_dir"])
            else:
                blocks = None
            self._add_key(key, blocks, vertices, main_blocks, fresh)
        for block, reused in main_blocks:
            if not reused:
                fresh.add(len(vertices))
            vertices.append(block)
        return vertices, fresh

    def _add_key(self, key: Any, blocks: Optional[list[Any]], vertices: list[Any], main_blocks: list[Any],
                 fresh: set[int]) -> None:
        """Unchanged definition key: its baseline vertices as they are (instances in place, main blocks deferred).
        Changed key: per block, reuse or re-expand."""
        e = self.e
        if blocks is None:
            if not self._key_has_changed_statement(key):
                for position in e.definition_entries[key]["vertices"]:
                    vertex = e._reused_vertex(position)
                    if is_expanded(vertex) and raw_tf_in_graph():
                        main_blocks.append((vertex, True))
                    else:
                        vertices.append(vertex)
                return
            # unchanged file, but a counted block of it has a new statement (e.g. its count variable lives in
            # another file): re-create the key's blocks and decide per block
            blocks = e._create_blocks(key, loads(e.pickled_definitions[key]), self.module_fields["source"],
                                      self.module_fields["external_modules_source_map"],
                                      self.module_fields["source_dir"])
        for block in blocks:
            if block.block_type == BlockType.MODULE and is_counted(block):
                raise IncrementalGraphUnsupported(f"module count/for_each in a changed file: {block.name}")
            if block.block_type == BlockType.DATA and is_expanded(block):
                raise IncrementalGraphUnsupported(f"data count/for_each expansion enabled: {block.name}")
            if not is_expanded(block):
                vertices.append(e._reuse_if_unchanged(block, fresh, len(vertices)))
                continue
            self._add_counted(block, vertices, main_blocks, fresh)

    def _add_counted(self, block: Any, vertices: list[Any], main_blocks: list[Any], fresh: set[int]) -> None:
        from checkov.terraform.diff_scan.baseline import creation_digest
        from checkov.terraform.diff_scan.expansions import block_key

        e = self.e
        key = block_key(block, e.root)
        statement = self.oracle.statement_for(key)
        baseline_positions = self.by_block.get(_block_key_from_expansion_key(key), [])
        main_position = next((p for p in baseline_positions if "[" not in _name_of(e.old_keys[p])), None)
        unchanged_block = main_position is not None and \
            self._pre_expansion_digest(e._reused_vertex(main_position)) == self._pre_expansion_digest(block) \
            if NEGATIVE_CONTROL != "stale_counted_block" else main_position is not None
        if unchanged_block and not self.oracle.statement_changed(key):
            for position in baseline_positions:
                vertex = e._reused_vertex(position)
                if position == main_position:
                    main_blocks.append((vertex, True))
                else:
                    vertices.append(vertex)
                    self.stats["instances_reused"] += 1
            self.stats["blocks_reused"] += 1
            return
        expanded = expand_block(block, statement)
        self.stats["blocks_reexpanded"] += 1
        for vertex in expanded[:-1] if raw_tf_in_graph() and statement else expanded:
            if raw_tf_in_graph() and vertex is block:
                continue
            vertices.append(e._reuse_if_unchanged(vertex, fresh, len(vertices)))
            self.stats["instances_created"] += 1
        main_blocks.append((block, False))


def _name_of(vertex_key: str) -> str:
    import json

    return json.loads(vertex_key)[3]


def _block_key_of_vertex_key(vertex_key: str) -> str:
    """A vertex key (`incremental_graph.vertex_key`) -> the identity of the block it was expanded from: same path and
    module chain, name without the instance index. Instances and their main block share it."""
    import json

    path, chain, block_type, name, *_ = json.loads(vertex_key)
    return json.dumps([path, [list(m) for m in chain], block_type, base_name(name)], sort_keys=True)


def _block_key_from_expansion_key(expansion_key: str) -> str:
    """An expansions.block_key (pre-expansion block) -> the same identity as _block_key_of_vertex_key."""
    import json

    path, chain, block_type, name = json.loads(expansion_key)
    return json.dumps([path, [list(m) for m in chain], block_type, base_name(name)], sort_keys=True)
