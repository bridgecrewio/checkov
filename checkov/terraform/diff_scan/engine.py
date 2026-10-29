"""Diff-files-only PR engine: the PR's pre-render graph from the baseline artifact plus the changed files only.

  1. definitions   parse each added/modified file once; fan a local-module file out to every instance key the baseline
                   loaded that directory under; drop the keys of deleted files. Module calls keep the baseline's
                   resolved instance list (a call whose source/instances would change is unsupported).
  2. vertices      Checkov creates vertices definition key by definition key in sorted key order (checked at baseline:
                   `order_matches_definitions`). Unchanged keys: the baseline's pre-render vertices are reused (one
                   unpickle each). Changed keys: blocks are created with Module.add_blocks; a block whose creation state
                   equals the baseline's is swapped for the reused baseline vertex.
  3. indexes       the name / module / block-type indexes and `source_module` are recomputed from the spliced vertex
                   list (index maintenance only: no parsing, no reference resolution).
  4. edges         an edge owner is rebuilt (Checkov's own _build_edges_for_vertex / _connect_module_provider_for_vertex)
                   when it is new or changed, when an index bucket it read at baseline changed, or when a provider alias
                   / resource type it mentions appeared or disappeared. Every other owner's edges are replayed from the
                   artifact (indices remapped through stable vertex keys), in Checkov's original edge order.
  5. passes        calculate_encryption_attribute runs on newly created vertices only (it is per-vertex).

Not supported (raises IncrementalGraphUnsupported, never silently rebuilt): count/for_each anywhere, changed tfvars /
TF_VAR_* inputs, new directories, added/removed/re-sourced module calls, non-.tf changes, parse errors.
"""
from __future__ import annotations

import json
import os
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Iterable, Iterator, Optional

from checkov.common.graph.graph_builder import Edge
from checkov.common.util.consts import RESOLVED_MODULE_ENTRY_NAME
from checkov.common.util.data_structures_utils import pickle_deepcopy
from checkov.terraform.graph_builder.foreach.consts import COUNT_STRING, FOREACH_STRING
from checkov.terraform.graph_builder.graph_components.block_types import BlockType
from checkov.terraform.graph_builder.graph_components.blocks import TerraformBlock
from checkov.terraform.graph_builder.graph_components.generic_resource_encryption import ENCRYPTION_BY_RESOURCE_TYPE
from checkov.terraform.graph_builder.graph_components.module import Module
from checkov.terraform.graph_builder.incremental_graph import IncrementalGraphUnsupported, ROOT, vertex_keys
from checkov.terraform.graph_builder.local_graph import TerraformLocalGraph
from checkov.terraform.modules.module_objects import TFDefinitionKey, TFModule
from checkov.terraform.modules.module_utils import clean_parser_types, serialize_definitions
from checkov.terraform.parser_utils import load_or_die_quietly

from checkov.terraform.diff_scan import lookups
from checkov.terraform.diff_scan.artifact import ARTIFACT_VERSION, loads
from checkov.terraform.diff_scan.artifact_store import IndexedDefinitionEntry
from checkov.terraform.diff_scan.baseline import aliases_signature, creation_digest, resource_types_of, tf_var_environment
from checkov.terraform.diff_scan.expansions import ExpansionOracle
from checkov.terraform.diff_scan.instance_update import InstanceSplicer, instance_update_enabled, is_expanded
from checkov.terraform.diff_scan.module_files import ModuleFileSetPlan
from checkov.terraform.diff_scan.units import pre_expansion_unit_graph
from checkov.terraform.diff_scan.graph_ops import set_edges
from checkov.terraform.diff_scan.recorder import BUILD_PHASE, PROVIDER_PHASE
from checkov.terraform.diff_scan.reparse import VirtualTree, parse_unit
from checkov.terraform.diff_scan.scanner_inputs import external_modules, is_external_module_path, var_files_from_env
from checkov.terraform.diff_scan.tfvars import HandleVariablesCall, is_ignored_by_checkov, is_terraform_file, is_variable_file, \
    replay, tfvar_blocks
from checkov.terraform.diff_scan.units import build_unit, has_count_or_foreach, unit_of_key, unit_of_vertex

FOREACH_BLOCK_TYPES = (BlockType.MODULE, BlockType.RESOURCE, BlockType.DATA)
NEGATIVE_CONTROL = os.getenv("DFO_NEGATIVE", "")
RESOURCE_LEVEL_UNITS_ENV = "CHECKOV_DIFF_RESOURCE_LEVEL_UNITS"
REUSE_EXPANSIONS_ENV = "CHECKOV_DIFF_REUSE_EXPANSIONS"
"""Test-only weakening of the engine, to prove the harness detects the errors it would cause:
  no_bucket_invalidation   unchanged owners never rebuild their edges (stale cross-file references)
  stale_module_fanout      a changed module file updates only its first instance (stale instances)
  stale_scoped_unit        a scoped (count/for_each) unit is rebuilt from the BASELINE definitions (change ignored)
  no_index_field_restore   spliced units lose their accumulated source_module / module_connections
  ignore_variable_inputs   tfvars / --var-file / TF_VAR_* changes are not recomputed (baseline tfvar vertices kept)
  no_external_change_detection  external module content changes (same address) are not detected
  ignore_deletions         deleted files are ignored (their vertices stay)
  no_global_token_units    units mentioning a resource type / alias that appeared or disappeared are spliced
  unit_local_lookups       scoped unit builds see only their own resource types / aliases
  no_module_fileset_rule   a module directory's file set changing does not re-parse its callers
  no_module_input_check    a missing external-module input is not refused
  no_relocation            the artifact is not relocated to the PR root
  relocation_breaks_aliasing  the first relocator (copies containers, breaks aliasing)
  no_reparse               units whose definition key set changed are not re-parsed (baseline module resolution)
  no_input_validation      the baseline-commit / complete-diff / configuration validation is skipped (inputs.py)
  stale_loop_end_state     frozen vertices keep their loop-end state instead of the final one (v3 encoded records)
  missing_section_file     a section of a v3 store cannot be read (fail closed expected)
  stale_expansion          Round 8: every recorded count/for_each statement is reused, even when its read closure changed
  stale_counted_block      Round 8: a counted block is reused whenever its statement is unchanged, even if its source changed
  unchanged_key_stale_instances  Round 8: an unchanged file's counted blocks are never re-expanded"""


@dataclass
class PreRenderReport:
    definition_keys: int = 0
    definition_keys_reparsed: int = 0
    files_parsed: list[str] = field(default_factory=list)
    files_deleted: list[str] = field(default_factory=list)
    vertices: int = 0
    vertices_reused: int = 0
    vertices_rebuilt: int = 0
    vertices_added: list[str] = field(default_factory=list)
    vertices_removed: list[str] = field(default_factory=list)
    vertices_changed: list[str] = field(default_factory=list)
    edges: int = 0
    edges_reused: int = 0
    edges_rebuilt: int = 0
    edge_owners_rebuilt: list[str] = field(default_factory=list)
    edge_owner_reasons: dict[str, int] = field(default_factory=dict)
    changed_buckets: list[str] = field(default_factory=list)
    module_instances: int = 0
    module_instances_reused: int = 0
    module_instances_updated: list[str] = field(default_factory=list)
    definitions_unpickled_for_post_render: int = 0
    global_tokens_changed: list[str] = field(default_factory=list)
    """resource types / provider aliases that appeared or disappeared (Checkov's global lookup lists)"""
    files_ignored: list[str] = field(default_factory=list)
    """changed files Checkov's Terraform directory scan never loads (.tf.json, non-Terraform files): accepted,
    contribute nothing"""
    files_parse_equivalent: list[str] = field(default_factory=list)
    """changed .tf files parse-equivalent to the baseline (CHECKOV_DIFF_SKIP_EQUIVALENT_FILES): treated as unchanged"""
    mode: str = "per-owner"
    """per-owner: every unit spliced, edges rebuilt per owner | scoped-units: changed units rebuilt by Checkov"""
    units_total: int = 0
    units_reused: int = 0
    scoped_units: dict[str, Any] = field(default_factory=dict)
    renamed_files: list[dict[str, str]] = field(default_factory=list)
    module_file_set: dict[str, Any] = field(default_factory=dict)
    """module directories whose file add / delete was handled per instance (no caller re-parse), and refusals"""
    """pure order-preserving renames applied to the artifact instead of re-parsing (rename.py)"""


@dataclass
class ChangeSet:
    changed: list[str]
    """absolute paths of added / modified files; their content is on disk"""
    deleted: list[str]
    """absolute paths of deleted files (renames / moves are a delete plus an add)"""


_LAZY_UNSET = object()


class LazyTerraformBlock(TerraformBlock):
    """A reused pre-render vertex initialized from its key string without unpickling `vertices[i]`. If a pre-render
    pass reads `attributes` / `config` / `id` / `source` / `has_dynamic_block` / `dynamic_attributes` / `foreach_attrs`
    before `restore_vertex` populates them from `rendered.vertices`, the pre-render pickle is loaded on demand."""

    __slots__ = ("_loader", "_loaded", "_rendered_loader", "dfo_key", "dfo_reused_unchanged",
                 "dfo_baseline_source_module", "dfo_baseline_sm_indices")

    def __init__(self, key: str, path: str, block_type: str, name: str,
                 source_module_object: Optional[TFModule], for_each_index: Any,
                 loader: Any) -> None:
        self.dfo_key = key
        self.dfo_reused_unchanged = True
        self._loader = loader
        self._rendered_loader: Any = None
        self._loaded = False
        self.path = path
        self.block_type = block_type
        self.name = name
        self.source_module_object = source_module_object
        self.for_each_index = for_each_index
        self.source_module: set[int] = set()
        self.module_connections: dict[str, list[int]] = {}
        self.changed_attributes: dict[str, list[Any]] = {}
        self.breadcrumbs: dict[str, list[dict[str, Any]]] = {}

    def set_rendered_loader(self, records: Any, decode: Any, key: str, by_key: dict[str, int], root: str,
                            swap: Any = None, graph: Any = None) -> None:
        self._loaded = False
        self._loader = None
        if os.getenv("DFO_NEGATIVE", "") == "lazy_vertex_wrong_record":
            key = next(iter(records))
        raw_bytes = records[key] if getattr(records, "_file", None) is not None and getattr(records._file, "closed", False) else None
        self._rendered_loader = (records, decode, key, by_key, root, swap, graph, raw_bytes)

    def _ensure_loaded(self) -> None:
        if self._loaded:
            return
        if self._rendered_loader is not None:
            self._loaded = True
            rl = self._rendered_loader
            self._rendered_loader = None
            from checkov.terraform.graph_builder.incremental_graph import (
                RESOLVED_SWAPS, _restore, _swap_resolved, restore_vertex
            )
            if isinstance(rl, tuple):
                records, decode, key, by_key, root, swap, graph, raw_bytes = rl
            else:
                graph = rl
                records, decode, root = graph._dfo_lazy_final_loader
                from checkov.terraform.graph_builder.incremental_graph import vertex_key
                key = self.dfo_key or vertex_key(self, root)
                by_key = None
                swap = RESOLVED_SWAPS.get(key)
                raw_bytes = None
            if hasattr(records, "_artifact"):
                records = records["vertices"]
            if os.getenv("DFO_NEGATIVE", "") == "lazy_vertex_wrong_record":
                key = next(iter(records))
            stored = raw_bytes if raw_bytes is not None else records[key]
            record = decode(stored) if decode is not None else stored
            if os.getenv("DFO_NEGATIVE", "") == "reread_final_state_as_loop_end":
                record = {**record, "attributes": record["loop_end"]["attributes"], "config": record["loop_end"]["config"]}
            map_for_v: Any = by_key
            if map_for_v is None and graph is not None:
                map_for_v = getattr(graph, "_dfo_by_key", None)
                if map_for_v is None:
                    map_for_v = getattr(graph, "_dfo_unit_key_to_pr", None)
                    if map_for_v is None:
                        map_for_v = {}
                        graph._dfo_unit_key_to_pr = map_for_v
            restore_vertex(self, record, map_for_v if map_for_v is not None else {}, root, skip_loop_end=True, graph=graph)
            self.attributes = _restore(record["attributes"], root)
            self.config = _restore(record["config"], root)
            if isinstance(self.config, dict) and self.block_type == BlockType.RESOURCE:
                for r_val in self.config.values():
                    if isinstance(r_val, dict):
                        for e_cfg in r_val.values():
                            if isinstance(e_cfg, dict) and isinstance(e_cfg.get("__start_line__"), list) \
                                    and isinstance(e_cfg.get("__end_line__"), list):
                                e_cfg["__start_line__"] = e_cfg["__start_line__"][0]
                                e_cfg["__end_line__"] = e_cfg["__end_line__"][0]
            if swap is not None:
                _swap_resolved(self, swap[1])
            if graph is not None:
                from checkov.common.graph.graph_builder import CustomAttributes
                from checkov.terraform.context_parsers.registry import parser_registry
                for attribute_key, breadcrumbs_list in self.changed_attributes.items():
                    hash_breadcrumbs = []
                    for breadcrumb in breadcrumbs_list:
                        v = graph.vertices[breadcrumb.vertex_id]
                        bdata = v.get_export_data()
                        bdata["module_connection"] = graph._determine_if_module_connection(breadcrumbs_list, v)
                        hash_breadcrumbs.append(bdata)
                    self.breadcrumbs[attribute_key] = hash_breadcrumbs
                if len(self.source_module) == 1:
                    v = self
                    source_module_data = []
                    while len(v.source_module) == 1:
                        idx = list(v.source_module)[0]
                        v = graph.vertices[idx]
                        module_data = v.get_export_data()
                        module_data["idx"] = idx
                        if hasattr(self, "source_module_object"):
                            module_data["source_module_object"] = v.source_module_object
                        source_module_data.append(module_data)
                    source_module_data.reverse()
                    self.breadcrumbs[CustomAttributes.SOURCE_MODULE] = source_module_data
                if self.attributes.get(CustomAttributes.TF_RESOURCE_ADDRESS) is None \
                        and self.block_type in parser_registry.context_parsers:
                    sm_bc = self.breadcrumbs.get(CustomAttributes.SOURCE_MODULE)
                    prefix = "".join(f"{m.get('type')}.{m.get('name')}." for m in sm_bc) if sm_bc else ""
                    cp = parser_registry.context_parsers[self.block_type]
                    ec_path = cp.get_entity_context_path(self.config)
                    res_id = ".".join(ec_path) if ec_path else self.name
                    addr = f"{prefix}{res_id}"
                    self.attributes[CustomAttributes.TF_RESOURCE_ADDRESS] = addr
                    v_ctx = self.config
                    for p_part in cp.get_entity_definition_path(self.config):
                        v_ctx = v_ctx.get(p_part, v_ctx)
                    v_ctx[CustomAttributes.TF_RESOURCE_ADDRESS] = addr
                if self.block_type == BlockType.RESOURCE and CustomAttributes.PROVIDER_ADDRESS not in self.attributes:
                    try:
                        graph._add_provider_attr_to_resource(self)
                    except Exception:  # noqa: S110
                        pass
            return
        if self._loader is None:
            return
        self._loaded = True
        loader = self._loader
        self._loader = None
        real = loads(loader[0]["vertices"][loader[1]]) if isinstance(loader, tuple) else loader()
        for slot in ("attributes", "config", "id", "source", "has_dynamic_block", "dynamic_attributes", "foreach_attrs"):
            try:
                object.__getattribute__(self, slot)
            except AttributeError:
                object.__setattr__(self, slot, getattr(real, slot, None))

    def _ensure_loaded_loop_end(self) -> None:
        if self._rendered_loader is not None:
            self._loaded = True
            rl = self._rendered_loader
            self._rendered_loader = None
            from checkov.terraform.graph_builder.incremental_graph import RESOLVED_SWAPS, restore_vertex
            if isinstance(rl, tuple):
                records, decode, key, by_key, root, swap, graph, raw_bytes = rl
            else:
                graph = rl
                records, decode, root = graph._dfo_lazy_final_loader
                from checkov.terraform.graph_builder.incremental_graph import vertex_key
                key = self.dfo_key or vertex_key(self, root)
                by_key = None
                raw_bytes = None
            if hasattr(records, "_artifact"):
                records = records["vertices"]
            map_for_v: Any = by_key
            if map_for_v is None and graph is not None:
                map_for_v = getattr(graph, "_dfo_by_key", None) or getattr(graph, "_dfo_unit_key_to_pr", None)
                if map_for_v is None:
                    map_for_v = {}
                    graph._dfo_unit_key_to_pr = map_for_v
            stored = raw_bytes if raw_bytes is not None else records[key]
            record = decode(stored) if decode is not None else stored
            restore_vertex(self, record, map_for_v if map_for_v is not None else {}, root, skip_loop_end=False, graph=graph)

    def mark_restored(self, id_val: str, source_val: str) -> None:
        self._loaded = True
        self._loader = None
        self._rendered_loader = None
        self.id = id_val
        self.source = source_val

    def __getattribute__(self, name: str) -> Any:
        if name in ("attributes", "config", "id", "source", "has_dynamic_block", "dynamic_attributes", "foreach_attrs",
                    "changed_attributes", "breadcrumbs"):
            if not object.__getattribute__(self, "_loaded"):
                object.__getattribute__(self, "_ensure_loaded")()
        return object.__getattribute__(self, name)

class _PickledDefinitionsView:
    """Dict-like view {TFDefinitionKey: pickled definition} backed by `definition_entries` so definition pickles are
    not read from disk (when `definitions` is an IndexedDefinitions) until a key is looked up."""

    def __init__(self, entries: dict[TFDefinitionKey, Any]) -> None:
        self._entries = entries

    def __getitem__(self, key: TFDefinitionKey) -> Any:
        return self._entries[key]["definition"]

    def get(self, key: TFDefinitionKey, default: Any = None) -> Any:
        return self._entries[key]["definition"] if key in self._entries else default

    def __contains__(self, key: object) -> bool:
        return key in self._entries

    def __iter__(self) -> Iterator[TFDefinitionKey]:
        return iter(self._entries)

    def __len__(self) -> int:
        return len(self._entries)

    def __bool__(self) -> bool:
        return bool(self._entries)

    def keys(self) -> Any:
        return self._entries.keys()

    def items(self) -> Iterator[tuple[TFDefinitionKey, Any]]:
        return ((k, d["definition"]) for k, d in self._entries.items())

    def values(self) -> Iterator[Any]:
        return (d["definition"] for d in self._entries.values())


def _definition_key(stored: Any) -> TFDefinitionKey:
    """A definitions entry's key: pickled, or already decoded by relocation (relocate._KeyRelocator)."""
    return loads(stored) if isinstance(stored, (str, bytes)) else stored


class LazyDefinitions(dict):  # type: ignore[type-arg]
    """module.temp_tf_definition for the post-render provider pass: baseline definitions are unpickled on first access."""

    def __init__(self, pickled: Any, parsed: dict[TFDefinitionKey, Any]) -> None:
        super().__init__()
        self._pickled = pickled
        self._parsed = parsed
        self.unpickled = 0

    def _raw(self, key: Any) -> Any:
        entry = self._pickled[key]
        return entry["definition"] if isinstance(entry, dict) and "definition" in entry or hasattr(entry, "_offset") else entry

    def _load(self, key: Any) -> Any:
        if key in self._parsed:
            return self._parsed[key]
        if key not in self._pickled:
            raise KeyError(key)
        self._parsed[key] = loads(self._raw(key))
        self.unpickled += 1
        return self._parsed[key]

    def get(self, key: Any, default: Any = None) -> Any:
        return self._load(key) if key in self else default

    def __getitem__(self, key: Any) -> Any:
        return self._load(key)

    def __contains__(self, key: object) -> bool:
        return key in self._parsed or key in self._pickled

    def __bool__(self) -> bool:
        return bool(self._parsed or self._pickled)

    def __len__(self) -> int:
        if hasattr(self, "_total_len"):
            return self._total_len
        return len(set(self._parsed) | set(self._pickled))

    def keys(self) -> Any:
        return sorted(set(self._parsed) | set(self._pickled))

    def __iter__(self) -> Any:
        return iter(self.keys())


def _has_module_expansion(definition: dict[str, Any]) -> bool:
    for call in definition.get(BlockType.MODULE, []):
        if isinstance(call, dict):
            for data in call.values():
                if isinstance(data, dict) and (COUNT_STRING in data or FOREACH_STRING in data):
                    return True
    return False


def _short_block(key: str) -> str:
    key = key.split(":", 1)[1] if key.startswith("module-level:") else key
    path, chain, block_type, name = json.loads(key)
    return "".join(f"module.{entry[1]}." for entry in chain) + f"{block_type}.{name}"


def _short(key: str) -> str:
    path, chain, block_type, name, *_ = json.loads(key)
    prefix = "".join(f"module.{entry[1]}." for entry in chain)
    return f"{prefix}{block_type}.{name}"


def _parse_file(path: str) -> dict[str, Any]:
    errors: dict[str, Exception] = {}
    data = load_or_die_quietly(path, errors)
    if errors or data is None:
        raise IncrementalGraphUnsupported(f"changed file does not parse: {path}: {errors}")
    return next(iter(serialize_definitions(clean_parser_types({TFDefinitionKey(path): data})).values()))


SKIP_EQUIVALENT_FILES_ENV = "CHECKOV_DIFF_SKIP_EQUIVALENT_FILES"


def skip_equivalent_files_enabled() -> bool:
    return os.getenv(SKIP_EQUIVALENT_FILES_ENV, "false").lower() == "true"


def _module_calls(definition: dict[str, Any]) -> dict[str, Any]:
    return {name: data for call in definition.get(BlockType.MODULE, []) if isinstance(call, dict)
            for name, data in call.items() if isinstance(data, dict)}


def _call_signature(data: dict[str, Any]) -> list[Any]:
    return [data.get("source"), data.get("version")]


class DiffEngine:
    def __init__(self, artifact: dict[str, Any], root: str, changes: ChangeSet) -> None:
        if artifact.get("version") != ARTIFACT_VERSION:
            raise IncrementalGraphUnsupported(f"artifact version {artifact.get('version')} != {ARTIFACT_VERSION}")
        self.a = artifact
        self.root = os.path.realpath(root)
        self.report = PreRenderReport()
        relevant = lambda p: is_terraform_file(p) or is_variable_file(p)  # noqa: E731
        self.report.files_ignored = sorted(os.path.relpath(p, self.root) for p in changes.changed + changes.deleted
                                           if not relevant(p))
        self.changes = ChangeSet(changed=[p for p in changes.changed if relevant(p)],
                                 deleted=[p for p in changes.deleted if relevant(p)])
        self.supplied_modules: list[str] = []
        self.old_keys: list[str] = []
        self.old_index: dict[str, int] = {}
        if "pre_keyed_definitions" in artifact:
            self.definition_entries = artifact["pre_keyed_definitions"]
            self.old_keys = artifact["keys"]
            self.old_index = {k: i for i, k in enumerate(self.old_keys)}
        else:
            raw_defs = artifact["definitions"]
            self.definition_entries = {_definition_key(d.pop("key") if isinstance(d, IndexedDefinitionEntry) else d["key"]): d
                                       for d in raw_defs}
            if hasattr(raw_defs, "_entries"):
                raw_defs._entries = []
            del raw_defs
            if not hasattr(artifact, "sizes"):
                self.old_keys = artifact["keys"]
                self.old_index = {k: i for i, k in enumerate(self.old_keys)}
        self._defs_by_unit: Optional[dict[str, list[tuple[TFDefinitionKey, Any]]]] = None
        self.pickled_definitions: Any = _PickledDefinitionsView(self.definition_entries)
        self._reused_vertex_cache: dict[int, Any] = {}
        self.instance_level_fallbacks: dict[str, str] = {}
        if "creation_digests" in getattr(artifact, "sizes", {}):
            pass
        elif "creation_digests" not in artifact:
            if not self.old_keys:
                self.old_keys = artifact["keys"]
                self.old_index = {k: i for i, k in enumerate(self.old_keys)}
            artifact["creation_digests"] = [creation_digest(self._reused_vertex(i), self.root)
                                            for i in range(len(self.old_keys))]
        elif len(artifact["creation_digests"]) < len(self.old_keys):
            for i in range(len(artifact["creation_digests"]), len(self.old_keys)):
                artifact["creation_digests"].append(creation_digest(self._reused_vertex(i), self.root))

    # ------------------------------------------------------------------------------------------- 0. preconditions

    def validate_inputs(self) -> None:
        self._check_supported()

    def _check_supported(self) -> None:
        """Fail closed on incomplete or unsupported inputs (never run a partial scan)."""
        if not self.a["units_isolated"]:
            raise IncrementalGraphUnsupported(f"baseline links cross root-module units: {self.a['cross_unit_links'][:3]}")
        for path in self.changes.changed:
            if not os.path.isfile(path):
                raise IncrementalGraphUnsupported(f"changed file listed but its content was not supplied: {path}")
        for path in self.changes.deleted:
            if os.path.exists(path):
                raise IncrementalGraphUnsupported(f"file listed as deleted but present in the payload: {path}")
        missing = sorted(set(self.a["variable_inputs"].get("external_modules", [])) - set(self.supplied_modules))
        if missing and NEGATIVE_CONTROL != "no_module_input_check":
            raise IncrementalGraphUnsupported(f"resolved external modules used by the baseline are missing from the "
                                              f"PR inputs: {missing}")

    # ------------------------------------------------------------------------------------------- 0b. reparse triggers

    def _variable_inputs_changed(self) -> bool:
        inputs = self.a["variable_inputs"]
        changed_files = [p for p in self.changes.changed + self.changes.deleted if is_variable_file(p)]
        return bool(changed_files) or tf_var_environment() != self.a["tf_var_environment"] \
            or (var_files_from_env(self.root) or []) != inputs["var_files"]

    def _recompute_tfvar_blocks(self, scratch: str, module_fields: dict[str, Any]) -> list[Any]:
        """Checkov's handle_variables replayed with the PR's variable inputs (stored contents for unchanged files)."""
        inputs = self.a["variable_inputs"]
        contents = {p: t for p, t in inputs["files"].items() if p not in self.changes.deleted}
        for path in self.changes.changed:
            if is_variable_file(path):
                with open(path, encoding="utf-8-sig") as f:
                    contents[path] = f.read()
        for path in var_files_from_env(self.root) or []:
            if path not in contents:
                raise IncrementalGraphUnsupported(f"--var-file not in the baseline or the change set: {path}")
        calls = [HandleVariablesCall(**c) for c in inputs["calls"]]
        known = {c.directory for c in calls}
        for path in contents:
            if os.path.dirname(path) not in known:
                raise IncrementalGraphUnsupported(f"variable file in a directory the baseline did not load: {path}")
        external_vars = replay(calls, contents, var_files_from_env(self.root), scratch)
        return tfvar_blocks(external_vars, module_fields["source"])

    def _call_targets(self, definition: dict[str, Any], key: TFDefinitionKey) -> set[tuple[str, str]]:
        return {(name, json.dumps(_call_signature(data), default=str)) for name, data in _module_calls(definition).items()}

    def _topology_changed_units(self, parsed: dict[TFDefinitionKey, Any], removed: set[TFDefinitionKey]) -> set[str]:
        """Units whose module calls were added / removed / re-sourced (their key set must be re-derived)."""
        units: set[str] = set()
        for key, definition in parsed.items():
            old = loads(self.pickled_definitions[key]) if key in self.pickled_definitions else {}
            if self._call_targets(definition, key) != self._call_targets(old, key):
                units.add(unit_of_key(key))
        for key in removed:
            if _module_calls(loads(self.pickled_definitions[key])):
                units.add(unit_of_key(key))
        return units

    # ------------------------------------------------------------------------------------------- 1. definitions

    def _instances_by_directory(self) -> dict[str, set[Any]]:
        instances: dict[str, set[Any]] = defaultdict(set)
        for key in self.pickled_definitions:
            instances[os.path.dirname(key.file_path)].add(key.tf_source_modules)
        return instances

    def _new_definitions(self) -> tuple[dict[TFDefinitionKey, Any], set[TFDefinitionKey], set[TFDefinitionKey]]:
        """(parsed definitions of changed keys, changed keys, removed keys). Files in directories the baseline never
        loaded are collected in self.new_directory_files (they need a unit re-parse)."""
        instances = self._instances_by_directory()
        parsed: dict[TFDefinitionKey, Any] = {}
        removed: set[TFDefinitionKey] = set()
        self.new_directory_files: dict[str, dict[str, Any]] = {}
        for path in self.changes.deleted:
            if is_variable_file(path) or NEGATIVE_CONTROL == "ignore_deletions":
                continue
            removed |= {k for k in self.pickled_definitions if k.file_path == path}
            self.report.files_deleted.append(os.path.relpath(path, self.root))
        for path in self.changes.changed:
            if is_variable_file(path):
                continue
            directory = os.path.dirname(path)
            if directory not in instances:
                self.new_directory_files[path] = _parse_file(path)
                self.report.files_parsed.append(os.path.relpath(path, self.root))
                continue
            definition = _parse_file(path)
            self.report.files_parsed.append(os.path.relpath(path, self.root))
            ordered = sorted(instances[directory], key=lambda m: json.dumps(lookups._chain(m, self.root)))
            if NEGATIVE_CONTROL == "stale_module_fanout":
                ordered = ordered[:1]
            for instance in ordered:
                key = TFDefinitionKey(file_path=path, tf_source_modules=instance)
                if definition:
                    parsed[key] = self._with_resolved_modules(key, definition)
                elif key in self.pickled_definitions:
                    removed.add(key)
        return parsed, set(parsed), removed - set(parsed)

    def drop_parse_equivalent_files(self) -> None:
        """Changed .tf files whose parsed definition (attributes and block line ranges, per module instance) equals the
        baseline's are removed from the GRAPH change set (`files_parse_equivalent`): the pre-render graph cannot
        differ. They stay in `check_changes`: comments, trailing text and line terminators reach findings through
        code blocks and skip comments, so their findings are re-evaluated from the new text like any changed file."""
        self.check_changes = ChangeSet(changed=list(self.changes.changed), deleted=list(self.changes.deleted))
        if not skip_equivalent_files_enabled():
            return
        instances = self._instances_by_directory()
        equivalent = {path for path in self.changes.changed
                      if is_terraform_file(path) and not is_variable_file(path)
                      and self._is_parse_equivalent(path, instances.get(os.path.dirname(path)))}
        if not equivalent:
            return
        self.changes.changed[:] = [p for p in self.changes.changed if p not in equivalent]
        self.report.files_parse_equivalent = sorted(os.path.relpath(p, self.root) for p in equivalent)

    def _is_parse_equivalent(self, path: str, instances: Optional[set[Any]]) -> bool:
        keys = [TFDefinitionKey(file_path=path, tf_source_modules=instance) for instance in instances or ()]
        if not keys or not all(key in self.pickled_definitions for key in keys):
            return False
        try:
            definition = _parse_file(path)
        except IncrementalGraphUnsupported:
            return False
        if not definition:
            return False
        return all(self._with_resolved_modules(key, definition) == loads(self.pickled_definitions[key]) for key in keys)

    def _with_resolved_modules(self, key: TFDefinitionKey, definition: dict[str, Any]) -> dict[str, Any]:
        """Module calls are resolved by the parser; a PR may change a call's arguments, not what it loads."""
        from checkov.common.util.data_structures_utils import pickle_deepcopy

        definition = pickle_deepcopy(definition)
        old_calls = _module_calls(loads(self.pickled_definitions[key])) if key in self.pickled_definitions else {}
        for name, data in _module_calls(definition).items():
            unchanged_target = name in old_calls and _call_signature(data) == _call_signature(old_calls[name])
            resolved = old_calls[name].get(RESOLVED_MODULE_ENTRY_NAME) if unchanged_target else None
            if resolved is not None:
                data[RESOLVED_MODULE_ENTRY_NAME] = resolved
        return definition

    # ------------------------------------------------------------------------------------------- 2. vertices

    def _reused_vertex(self, old_index: int, unit: Optional[str] = None) -> Any:
        if old_index not in self._reused_vertex_cache:
            if self.old_keys:
                key = self.old_keys[old_index]
            elif unit is not None and unit in getattr(self, "_keys_by_unit", {}):
                pos_u_map = getattr(self, "_pos_u_by_unit", None)
                if pos_u_map is None:
                    pos_u_map = {}
                    self._pos_u_by_unit = pos_u_map
                if unit not in pos_u_map:
                    pos_u_map[unit] = {oi: pi for pi, oi in enumerate(self._old_by_unit[unit])}
                pos_u = pos_u_map[unit][old_index]
                key = self._keys_by_unit[unit][pos_u]
            else:
                key = self.a["keys"][old_index]
            identity = json.loads(key)
            block_type = identity[2]
            if block_type == BlockType.TF_VARIABLE or not (hasattr(self.a.get("vertices"), "_offsets")
                                                           or hasattr(self.a.get("vertices"), "_base")):
                v = loads(self.a["vertices"][old_index])
                self._reused_vertex_cache[old_index] = v
            else:
                chain_cache: dict[Any, Optional[TFModule]] = getattr(self, "_chain_cache", {})
                if not hasattr(self, "_chain_cache"):
                    self._chain_cache = chain_cache
                chain_raw = identity[1]
                chain_key = tuple((m[0], m[1], str(m[2])) for m in chain_raw)
                if chain_key not in chain_cache:
                    mod: Optional[TFModule] = None
                    for m_path, m_name, m_idx in chain_raw:
                        parsed_idx: Any = None if m_idx in (None, "None") else (int(m_idx) if str(m_idx).isnumeric() else m_idx)
                        mod = TFModule(path=sys.intern(m_path.replace(ROOT, self.root)), name=sys.intern(m_name),
                                       nested_tf_module=mod, foreach_idx=parsed_idx)
                    chain_cache[chain_key] = mod
                path = sys.intern(identity[0].replace(ROOT, self.root))
                name = identity[3]
                fe_idx = identity[4]
                if getattr(self, "_is_splicing_unchanged", False):
                    base_a = getattr(self.a, "_base", self.a)
                    block = LazyTerraformBlock(
                        key=None, path=path, block_type=sys.intern(block_type), name=name,
                        source_module_object=chain_cache[chain_key], for_each_index=fe_idx,
                        loader=(base_a, old_index),
                    )
                    block.dfo_baseline_source_module = None
                    block.dfo_baseline_sm_indices = None
                    return block
                base_a = getattr(self.a, "_base", self.a)
                g_pos = self.a.get("global_positions")
                real_idx = g_pos[old_index] if g_pos is not None else old_index
                block = LazyTerraformBlock(
                    key=key, path=path, block_type=sys.intern(block_type), name=name,
                    source_module_object=chain_cache[chain_key], for_each_index=fe_idx,
                    loader=(base_a, real_idx),
                )
                if unit is not None and unit in getattr(self, "_mc_by_unit", {}):
                    pos_u_map = getattr(self, "_pos_u_by_unit", None)
                    if pos_u_map is None:
                        pos_u_map = {}
                        self._pos_u_by_unit = pos_u_map
                    if unit not in pos_u_map:
                        pos_u_map[unit] = {oi: pi for pi, oi in enumerate(self._old_by_unit[unit])}
                    u_pos_dict = pos_u_map[unit]
                    pos_u = u_pos_dict[old_index]
                    mc = self._mc_by_unit[unit][pos_u]
                    sm = self._sm_by_unit[unit][pos_u]
                    old_keys_ref = self._keys_by_unit[unit]
                    block.dfo_baseline_source_module = {
                        old_keys_ref[u_pos_dict[i]] for i in sm if i in u_pos_dict
                    } if sm else None
                else:
                    mc = self.a["module_connections"][old_index] if "module_connections" in self.a else {}
                    sm = self.a["source_module"][old_index] if "source_module" in self.a else []
                    old_keys_ref = self.old_keys or self.a["keys"]
                    block.dfo_baseline_source_module = {old_keys_ref[i] for i in sm} if sm else None
                block.dfo_baseline_sm_indices = _LAZY_UNSET
                if mc:
                    block.module_connections = {a: list(ids) for a, ids in mc.items()}
                self._reused_vertex_cache[old_index] = block
        return self._reused_vertex_cache[old_index]

    def _create_blocks(self, key: TFDefinitionKey, definition: dict[str, Any], source: str,
                       external_map: dict[Any, Any], source_dir: str) -> list[Any]:
        from checkov.common.util.data_structures_utils import pickle_deepcopy

        module = Module(source_dir=source_dir, external_modules_source_map=external_map)
        blocks = pickle_deepcopy(definition)
        for block_type in blocks:
            module.add_blocks(block_type, blocks[block_type], key, source)
        return module.blocks

    def _splice_vertices(self, parsed: dict[TFDefinitionKey, Any], changed: set[TFDefinitionKey],
                         removed: set[TFDefinitionKey], module_fields: dict[str, Any]) -> tuple[list[Any], set[int]]:
        """New vertex list in Checkov order, and the positions of freshly created (not reused) vertices.
        tfvar vertices come first (add_tfvars runs before the definitions are added): the baseline's, or the PR's
        recomputed ones when variable inputs changed (`self.unit_tfvar_blocks`), reused when unchanged."""
        fresh: set[int] = set()
        replacement = getattr(self, "unit_tfvar_blocks", None)
        if replacement is None:
            vertices = [self._reused_vertex(i) for i in self.a["tfvar_vertices"]]
        else:
            vertices = []
            for block in replacement:
                vertices.append(self._reuse_if_unchanged(pickle_deepcopy(block), fresh, len(vertices)))
        all_keys = sorted((set(self.pickled_definitions) - removed) | changed)
        for key in all_keys:
            if key not in changed:
                vertices.extend(self._reused_vertex(i) for i in self.definition_entries[key]["vertices"])
                continue
            blocks = self._create_blocks(key, parsed[key], module_fields["source"],
                                         module_fields["external_modules_source_map"], module_fields["source_dir"])
            for block in blocks:
                if block.block_type in FOREACH_BLOCK_TYPES and (FOREACH_STRING in block.attributes
                                                                or COUNT_STRING in block.attributes):
                    raise IncrementalGraphUnsupported(f"count/for_each block in a changed file: {block.name}")
                vertices.append(self._reuse_if_unchanged(block, fresh, len(vertices)))
        return vertices, fresh

    def _ensure_old_keys(self) -> None:
        if not self.old_keys:
            self.old_keys = self.a["keys"]
            self.old_index = {k: i for i, k in enumerate(self.old_keys)}

    def _reuse_if_unchanged(self, block: Any, fresh: set[int], position: int) -> Any:
        self._ensure_old_keys()
        key = lookups_vertex_key(block, self.root)
        old = self.old_index.get(key)
        if old is not None and self.a["creation_digests"][old] == creation_digest(block, self.root):
            return self._reused_vertex(old)
        fresh.add(position)
        return block

    # ------------------------------------------------------------------------------------------- 3 + 4. edges

    def _changed_buckets(self, new_keys: list[str], vertices: list[Any], fresh: set[int]) -> set[str]:
        self._ensure_old_keys()
        new_set, old_set = set(new_keys), set(self.old_keys)
        buckets: set[str] = set()
        for key in (new_set ^ old_set):
            buckets.update(lookups.buckets_from_vertex_key(key))
        for position in fresh:
            key = new_keys[position]
            old = self.old_index.get(key)
            if old is not None and self.a["fingerprints"][old] != lookups.edge_fingerprint(vertices[position]):
                buckets.update(lookups.buckets_from_vertex_key(key))
        return buckets

    def _global_tokens_changed(self, graph: TerraformLocalGraph) -> set[str]:
        g = getattr(self, "_global_parsed_and_removed", None)
        if getattr(self, "_cached_old_types", None) is None:
            def_entries = g[2] if g is not None else self.definition_entries
            self._cached_old_types = {t for d in def_entries.values() for t in d["resource_types"]}
        old_types = self._cached_old_types
        new_types, pr_aliases = self._pr_global_tokens(self._last_parsed, self._last_removed)
        old_aliases = {name for name, _ in self.a["aliases"]}
        new_aliases = {name for name, _ in pr_aliases}
        tokens = (old_types ^ new_types) | (old_aliases ^ new_aliases)
        if {tuple(a) for a in self.a["aliases"]} != pr_aliases:
            tokens |= old_aliases | new_aliases
        return tokens

    def _pr_global_tokens(self, parsed: dict[TFDefinitionKey, Any], removed: set[TFDefinitionKey]) \
            -> tuple[set[str], set[tuple[str, str]]]:
        """Checkov's GLOBAL lookup lists as of the PR: resource types (Module.resources_types) and provider aliases
        (_get_aliases). Computed from definitions only (stored for unchanged keys, parsed for changed ones)."""
        g = getattr(self, "_global_parsed_and_removed", None)
        if g is not None:
            if len(g) >= 6:
                return set(g[5]), set(g[6])
            parsed, removed, def_entries, old_aliases_list, old_alias_keys = g
        else:
            def_entries, old_aliases_list, old_alias_keys = self.definition_entries, self.a["aliases"], self.a["alias_keys"]
        cache_attr = "_cached_pr_global_tokens"
        if getattr(self, "_global_parsed_and_removed", None) is None:
            cached = getattr(self, cache_attr, None)
            if cached is not None and cached[0] == id(parsed) and cached[1] == id(removed):
                return set(cached[2]), set(cached[3])
        kept = {k for k in def_entries if k not in removed and k not in parsed}
        types = {t for k in kept for t in def_entries[k]["resource_types"]}
        types |= {t for d in parsed.values() for t in resource_types_of(d)}
        aliases = {tuple(a) for a in old_aliases_list
                   if any(key in kept for key in (loads(k) for k in old_alias_keys.get(a[0], [])))}
        for definition in parsed.values():
            for provider in definition.get(BlockType.PROVIDER, []):
                for name, attrs in provider.items():
                    if isinstance(attrs, dict) and attrs.get("alias"):
                        aliases.add((f"{name}.{attrs['alias'][0]}", BlockType.PROVIDER))
        if getattr(self, "_global_parsed_and_removed", None) is None:
            setattr(self, cache_attr, (id(parsed), id(removed), set(types), set(aliases)))
        return types, aliases

    def _units_reading_changed_tokens(self, parsed: dict[TFDefinitionKey, Any],
                                      removed: set[TFDefinitionKey]) -> set[str]:
        """UNIT ISOLATION: the resource-type and provider-alias lists are global, so a type/alias that appears or
        disappears ANYWHERE can change the edges (and rendering) of a vertex in an unchanged unit that mentions it.
        Such units are touched (per-owner, or scoped if they contain count/for_each) instead of spliced."""
        cached_u = getattr(self, "_cached_token_units", None)
        if cached_u is not None and cached_u[0] == id(parsed) and cached_u[1] == id(removed):
            return set(cached_u[2])
        types, aliases = self._pr_global_tokens(parsed, removed)
        if getattr(self, "_cached_old_types", None) is None:
            self._cached_old_types = {t for d in self.definition_entries.values() for t in d["resource_types"]}
        old_types = self._cached_old_types
        old_aliases = {tuple(a) for a in self.a["aliases"]}
        tokens = (types ^ old_types) | {n for n, _ in aliases ^ old_aliases}
        if not tokens or NEGATIVE_CONTROL == "no_global_token_units":
            self._cached_token_units = (id(parsed), id(removed), set())
            return set()
        units: set[str] = set()
        raw_verts = self.a["vertices"]
        if hasattr(raw_verts, "_offsets"):
            token_bytes = [t.encode() for t in tokens]
            old_by_u = getattr(self, "_old_by_unit", None)
            if old_by_u is None:
                old_by_u = defaultdict(list)
                for index, unit in enumerate(self.a["unit_by_vertex"]):
                    old_by_u[unit].append(index)
                self._old_by_unit = old_by_u
            f_obj = raw_verts._file
            offsets = raw_verts._offsets
            for unit, idxs in old_by_u.items():
                if not idxs:
                    continue
                is_contig = idxs[-1] - idxs[0] + 1 == len(idxs)
                if is_contig:
                    start_off = offsets[idxs[0]][0]
                    end_off = offsets[idxs[-1]][0] + offsets[idxs[-1]][1]
                    f_obj.seek(start_off)
                    chunk = f_obj.read(end_off - start_off)
                    if not any(tb in chunk for tb in token_bytes):
                        continue
                for index in idxs:
                    if any(tb in raw_verts[index] for tb in token_bytes) and _mentions(self._reused_vertex(index), tokens):
                        units.add(unit)
                        break
        else:
            old_by_u = getattr(self, "_old_by_unit", None)
            if old_by_u is not None:
                for unit, idxs in old_by_u.items():
                    for index in idxs:
                        if _mentions(self._reused_vertex(index), tokens):
                            units.add(unit)
                            break
            else:
                for index, unit in enumerate(self.a["unit_by_vertex"]):
                    if unit in units:
                        continue
                    if _mentions(self._reused_vertex(index), tokens):
                        units.add(unit)
        self.report.global_tokens_changed = sorted(tokens)
        self._cached_token_units = (id(parsed), id(removed), set(units))
        return units

    def _owners_to_rebuild(self, graph: TerraformLocalGraph, new_keys: list[str], fresh: set[int]) -> dict[int, str]:
        buckets = self._changed_buckets(new_keys, graph.vertices, fresh)
        self.report.changed_buckets = sorted(buckets)
        tokens = self._global_tokens_changed(graph)
        if NEGATIVE_CONTROL == "no_bucket_invalidation":
            buckets, tokens = set(), set()
        reasons: dict[int, str] = {i: "vertex new or changed" for i in fresh}
        for position, key in enumerate(new_keys):
            if position in reasons:
                continue
            old = self.old_index[key]
            if buckets & set(self.a["probes"].get(str(old), [])):
                reasons[position] = "read an index bucket that changed"
            elif tokens:
                v_pos = graph.vertices[position]
                if isinstance(v_pos, LazyTerraformBlock) and not v_pos._loaded and isinstance(v_pos._loader, tuple):
                    raw_b = v_pos._loader[0]["vertices"][v_pos._loader[1]]
                    # pickle stores str as UTF-8, so the shortcut holds for raw pickles only (v3 store); a v2
                    # artifact holds base64 text, where a token's absence proves nothing.
                    if isinstance(raw_b, bytes) and not any(t.encode() in raw_b for t in tokens):
                        continue
                if _mentions(v_pos, tokens):
                    reasons[position] = "mentions an added/removed resource type or provider alias"
        return reasons

    def _replayed_edges(self, new_keys: list[str]) -> dict[tuple[int, str], list[tuple[int, int, str]]]:
        new_index = {k: i for i, k in enumerate(new_keys)}
        replay: dict[tuple[int, str], list[tuple[int, int, str]]] = defaultdict(list)
        for origin, dest, label, owner, phase in self.a["edges"]:
            owner_key = self.old_keys[owner]
            if owner_key not in new_index:
                continue
            replay[(new_index[owner_key], phase)].append(
                (new_index.get(self.old_keys[origin], -1), new_index.get(self.old_keys[dest], -1), label))
        return replay

    def _build_edges(self, graph: TerraformLocalGraph, new_keys: list[str], rebuild: dict[int, str]) -> None:
        replay = self._replayed_edges(new_keys)
        _, pr_aliases = self._pr_global_tokens(self._last_parsed, self._last_removed)
        aliases = {n: {"block_type_": b} for n, b in pr_aliases}
        resources_types = graph.get_resources_types_in_graph()
        for position, vertex in enumerate(graph.vertices):
            if position in rebuild:
                before = len(graph.edges)
                graph._build_edges_for_vertex(position, vertex, aliases, resources_types)
                graph._build_virtual_resources_edges(position, vertex)
                self.report.edges_rebuilt += len(graph.edges) - before
                built_1 = [(e.origin, e.dest, e.label) for e in graph.edges[before:]]
                if built_1 != replay.get((position, BUILD_PHASE), []):
                    self._edge_tuples_identical_to_baseline = False
            else:
                self._append(graph, replay.get((position, BUILD_PHASE), []), new_keys[position])
        for position in list(graph.out_edges):
            if position in rebuild:
                before = len(graph.edges)
                graph._connect_module_provider_for_vertex(position, graph.out_edges[position])
                self.report.edges_rebuilt += len(graph.edges) - before
                built_2 = [(e.origin, e.dest, e.label) for e in graph.edges[before:]]
                if built_2 != replay.get((position, PROVIDER_PHASE), []):
                    self._edge_tuples_identical_to_baseline = False
            else:
                self._append(graph, replay.get((position, PROVIDER_PHASE), []), new_keys[position])
        if getattr(self, "_edge_tuples_identical_to_baseline", True):
            for position in range(len(graph.vertices)):
                if position not in rebuild and isinstance(graph.vertices[position], LazyTerraformBlock):
                    if getattr(graph.vertices[position], "dfo_baseline_sm_indices", _LAZY_UNSET) == _LAZY_UNSET:
                        if {new_keys[i] for i in graph.vertices[position].source_module} \
                                == (getattr(graph.vertices[position], "dfo_baseline_source_module", None) or set()):
                            graph.vertices[position].dfo_baseline_sm_indices = set(graph.vertices[position].source_module)

    def _append(self, graph: TerraformLocalGraph, edges: Iterable[tuple[int, int, str]], owner_key: str) -> None:
        for origin, dest, label in edges:
            if origin < 0 or dest < 0:
                raise RuntimeError(f"replayed edge of unchanged owner {owner_key} points to a removed vertex")
            edge = Edge(origin, dest, label)
            graph.edges.append(edge)
            graph.out_edges[origin].append(edge)
            graph.in_edges[dest].append(edge)
            self.report.edges_reused += 1

    def _remap_module_connections(self, graph: TerraformLocalGraph, new_keys: list[str], fresh: set[int],
                                  rebuild: dict[int, str]) -> None:
        """A reused vertex's module_connections hold BASELINE-graph indices (the pickled vertex); map them through
        their stable keys. In a unit sub-artifact the baseline index is global: map it to the unit position first."""
        new_index = {k: i for i, k in enumerate(new_keys)}
        local_of_global = {g: p for p, g in enumerate(self.a.get("global_positions", []))}
        for position, vertex in enumerate(graph.vertices):
            if position in fresh:
                continue
            if position in rebuild:
                vertex.module_connections = {}
                continue
            vertex.module_connections = {
                attr: [new_index[self.old_keys[local_of_global.get(i, i) if local_of_global else i]] for i in ids]
                for attr, ids in vertex.module_connections.items()}

    # ------------------------------------------------------------------------------------------- 5. passes

    @staticmethod
    def _encrypt_fresh(graph: TerraformLocalGraph, fresh: set[int]) -> None:
        from checkov.common.graph.graph_builder import CustomAttributes

        manager = graph._graph_resource_encryption_manager
        manager.set_encription_by_resource_type(ENCRYPTION_BY_RESOURCE_TYPE)
        for position in sorted(fresh):
            vertex = graph.vertices[position]
            if vertex.block_type != BlockType.RESOURCE:
                continue
            result = manager.get_encryption_result(vertex)
            if result:
                vertex.attributes[CustomAttributes.ENCRYPTION] = result.encrypted
                vertex.attributes[CustomAttributes.ENCRYPTION_DETAILS] = result.reason

    # ------------------------------------------------------------------------------------------- entry point

    def build(self) -> TerraformLocalGraph:
        self._check_supported()
        module_fields = loads(self.a["module"])
        parsed, changed, removed = self._new_definitions()
        reparse = self._reparse_reasons(parsed, removed, module_fields)
        self.report.module_file_set = getattr(self, "module_file_set_report", {})
        changed = set(parsed)
        if reparse:
            self.extra_source_map: dict[Any, str] = {}
            graph = self._build_with_reparsed_units(parsed, changed, removed, module_fields, reparse)
            graph.module.external_modules_source_map = {**module_fields["external_modules_source_map"],
                                                        **self.extra_source_map}
        elif (scoped := self._scoped_units(parsed, changed, removed)) or self.a["foreach_ran"] \
                or self._tfvar_changed_units() or self._units_reading_changed_tokens(parsed, removed):
            graph = self._build_with_scoped_units(parsed, changed, removed, module_fields, scoped)
        else:
            vertices, fresh = self._splice_vertices(parsed, changed, removed, module_fields)
            graph = self._per_owner_graph(vertices, fresh, parsed, changed, removed, module_fields)
        _, pr_aliases = self._pr_global_tokens(getattr(self, "_last_parsed", parsed),
                                               getattr(self, "_last_removed", removed))
        graph.dfo_aliases = {n: {"block_type_": b} for n, b in pr_aliases}  # type: ignore[attr-defined]
        base_edge_cnt = getattr(self, "_baseline_edge_count", None)
        if base_edge_cnt is None:
            base_edge_cnt = len(self.a["edges"])
        graph.dfo_pre_render_edges_unchanged = (  # type: ignore[attr-defined]
            not self.report.vertices_added
            and not self.report.vertices_removed
            and len(graph.edges) == base_edge_cnt
            and all(u.get("mode") in ("per-owner", "instance-level") for u in self.report.scoped_units.values())
            and getattr(self, "_edge_tuples_identical_to_baseline", True)
        )
        graph.dfo_replayed_edges_unchanged = bool(getattr(self, "touched_units", None))  # type: ignore[attr-defined]
        if graph.dfo_pre_render_edges_unchanged or graph.dfo_replayed_edges_unchanged:
            from checkov.terraform.graph_builder.incremental_graph import _LAZY_SM_UNSET, pre_render_digest, vertex_key
            pre_digests: dict[str, str] = {}
            old_keys_list = None
            non_reused_indices = [
                idx_v for idx_v, v in enumerate(graph.vertices)
                if not getattr(v, "dfo_reused_unchanged", False)
                or (getattr(v, "dfo_baseline_sm_indices", _LAZY_SM_UNSET) != v.source_module
                    and {vertex_key(graph.vertices[j], self.root) for j in v.source_module}
                    != (getattr(v, "dfo_baseline_source_module", None) or set()))
            ]
            if len(non_reused_indices) <= 200:
                for idx_v in non_reused_indices:
                    v = graph.vertices[idx_v]
                    k = vertex_key(v, self.root)
                    u_v = unit_of_vertex(v)
                    keys_u = getattr(self, "_keys_by_unit", {}).get(u_v)
                    verts_u = getattr(self, "_old_by_unit", {}).get(u_v)
                    pos_u_map = getattr(self, "_pos_u_by_unit", {})
                    key_u_map = getattr(self, "_key_u_by_unit", None)
                    if key_u_map is None:
                        key_u_map = {}
                        self._key_u_by_unit = key_u_map
                    if keys_u is not None and u_v not in key_u_map:
                        key_u_map[u_v] = {ku: pi for pi, ku in enumerate(keys_u)}
                    if keys_u is not None and verts_u is not None and k in key_u_map.get(u_v, {}):
                        pos_in_u = key_u_map[u_v][k]
                        old_i = verts_u[pos_in_u]
                        old_v = loads(self.a["vertices"][old_i])
                        sm_u = getattr(self, "_sm_by_unit", {}).get(u_v)
                        raw_sm = sm_u[pos_in_u] if sm_u is not None else self.a["source_module"][old_i]
                        if u_v not in pos_u_map:
                            pos_u_map[u_v] = {oi: pi for pi, oi in enumerate(verts_u)}
                        u_pos_dict = pos_u_map[u_v]
                        old_v.source_module = {u_pos_dict[si] for si in raw_sm if si in u_pos_dict}
                        pre_digests[k] = pre_render_digest(old_v, self.root, keys_u)
                    elif keys_u is None and not self.old_keys:
                        if old_keys_list is None:
                            old_keys_list = self.old_keys or self.a["keys"]
                        old_idx_map = self.old_index or {ok: oi for oi, ok in enumerate(old_keys_list)}
                        old_i = old_idx_map.get(k)
                        if old_i is not None:
                            old_v = loads(self.a["vertices"][old_i])
                            old_v.source_module = set(self.a["source_module"][old_i])
                            pre_digests[k] = pre_render_digest(old_v, self.root, old_keys_list)
                graph.dfo_pre_render_digests = pre_digests  # type: ignore[attr-defined]
            else:
                graph.dfo_pre_render_digests = None  # type: ignore[attr-defined]
            touched_u_set = set(getattr(self, "touched_units", ()))
            if touched_u_set:
                unit_key_to_pr: dict[str, int] = {}
                rebuilt_offsets = getattr(self, "_rebuilt_unit_offsets", {})
                if rebuilt_offsets:
                    for u_t, (off_s, off_e) in rebuilt_offsets.items():
                        for idx_v in range(off_s, off_e):
                            unit_key_to_pr[vertex_key(graph.vertices[idx_v], self.root)] = idx_v
                else:
                    for idx_v, v in enumerate(graph.vertices):
                        if unit_of_vertex(v) in touched_u_set:
                            unit_key_to_pr[vertex_key(v, self.root)] = idx_v
                graph._dfo_unit_key_to_pr = unit_key_to_pr  # type: ignore[attr-defined]
                if not graph.dfo_pre_render_edges_unchanged:
                    old_touched_keys = {
                        ku for u_t in touched_u_set for ku in getattr(self, "_keys_by_unit", {}).get(u_t, ())
                    }
                    graph.dfo_removed_keys = sorted(old_touched_keys - set(unit_key_to_pr))  # type: ignore[attr-defined]
                    graph.dfo_rebuilt_unit_offsets = list(rebuilt_offsets.values())  # type: ignore[attr-defined]
                    old_u_edges: set[tuple[str, str, str]] = set()
                    for u_t in touched_u_set:
                        keys_u = getattr(self, "_keys_by_unit", {}).get(u_t, [])
                        verts_u = getattr(self, "_old_by_unit", {}).get(u_t, [])
                        pos_u_dict = getattr(self, "_pos_u_by_unit", {}).get(u_t) or {oi: pi for pi, oi in enumerate(verts_u)}
                        for er in getattr(self, "_edges_by_unit", {}).get(u_t, ()):
                            if er[0] in pos_u_dict and er[1] in pos_u_dict:
                                old_u_edges.add((keys_u[pos_u_dict[er[0]]], keys_u[pos_u_dict[er[1]]], er[2]))
                    graph.dfo_old_touched_edges = old_u_edges  # type: ignore[attr-defined]
        return graph

    def _per_owner_graph(self, vertices: list[Any], fresh: set[int], parsed: dict[TFDefinitionKey, Any],
                         changed: set[TFDefinitionKey], removed: set[TFDefinitionKey],
                         module_fields: dict[str, Any]) -> TerraformLocalGraph:
        self._ensure_old_keys()
        self._last_parsed, self._last_removed = parsed, removed
        module = Module(source_dir=module_fields["source_dir"],
                        external_modules_source_map=module_fields["external_modules_source_map"])
        module.source = module_fields["source"]
        module.blocks = vertices
        lazy_filter = os.getenv("CHECKOV_INCREMENTAL_LAZY_FINAL_STATE", "false").lower() == "true"
        kept = {
            k: d for k, d in self.definition_entries.items()
            if k not in removed and k not in changed
            and (not lazy_filter or not isinstance(d, dict) or d.get("has_provider_or_module", True))
        }
        module.temp_tf_definition = LazyDefinitions(kept, dict(parsed))
        module.temp_tf_definition._total_len = len(
            (set(self.definition_entries) - set(removed)) | set(parsed)
        )
        pr_types, _ = self._pr_global_tokens(parsed, removed)
        module.resources_types = set(pr_types)
        graph = TerraformLocalGraph(module)
        graph.vertices = vertices
        for vertex in vertices:
            vertex.source_module = set()
        graph._arrange_graph_data()
        graph.get_module_vertices_mapping()
        new_keys = vertex_keys(graph, self.root)
        rebuild = self._owners_to_rebuild(graph, new_keys, fresh)
        self._remap_module_connections(graph, new_keys, fresh, rebuild)
        self._build_edges(graph, new_keys, rebuild)
        self._encrypt_fresh(graph, fresh)
        self._fill_report(graph, new_keys, fresh, rebuild, changed, len(parsed))
        self._definitions = module.temp_tf_definition
        return graph

    # ------------------------------------------------------------------------------------------- Phase B: reparse

    def _baseline_directories(self) -> dict[str, str]:
        """Every directory the baseline loaded -> 'unit' (a root unit) or 'module' (only loaded through a call)."""
        kinds: dict[str, str] = {}
        for key in self.pickled_definitions:
            directory = os.path.dirname(key.file_path)
            kind = "unit" if key.tf_source_modules is None else "module"
            kinds[directory] = "unit" if kinds.get(directory) == "unit" else kind
        return kinds

    def _local_call_targets(self, definitions: dict[TFDefinitionKey, Any]) -> dict[str, set[str]]:
        """caller directory -> local module directories it calls (only definitions with no module chain or chains:
        a call is resolved relative to the file holding it)."""
        targets: dict[str, set[str]] = defaultdict(set)
        for key, definition in definitions.items():
            for data in _module_calls(definition).values():
                source = (data.get("source") or [None])[0]
                if isinstance(source, str) and source.startswith(("./", "../")):
                    targets[os.path.dirname(key.file_path)].add(
                        os.path.normpath(os.path.join(os.path.dirname(key.file_path), source)))
        return targets

    def _pr_definitions_by_file(self, parsed: dict[TFDefinitionKey, Any], removed: set[TFDefinitionKey]) \
            -> dict[str, Any]:
        """One definition per repository file as of the PR (module-instance copies collapsed)."""
        by_file: dict[str, Any] = {}
        gone = {k.file_path for k in removed} | set(self.changes.deleted)
        for key, value in self.pickled_definitions.items():
            if key.file_path not in gone and key.file_path not in by_file:
                by_file[key.file_path] = value
        for key, definition in parsed.items():
            by_file[key.file_path] = definition
        by_file.update(self.new_directory_files)
        return {path: (loads(v) if isinstance(v, (str, bytes)) else v) for path, v in by_file.items()}

    def _module_file_set_changed_units(self, parsed: dict[TFDefinitionKey, Any],
                                       removed: set[TFDefinitionKey]) -> set[str]:
        """A module call's `__resolved__` lists the definition keys (one per FILE) of the module instance it loads, and
        it is part of the caller vertex's config. When a file is added to / removed from a directory loaded as a
        module, every caller's `__resolved__` changes, so the units calling it need their keys re-derived."""
        loaded_as_module = {os.path.dirname(k.file_path) for k in self.pickled_definitions if k.tf_source_modules}
        old_files = {k.file_path for k in self.pickled_definitions}
        directories = {os.path.dirname(k.file_path) for k in removed if k.tf_source_modules}
        directories |= {os.path.dirname(k.file_path) for k in parsed
                        if k.tf_source_modules and k.file_path not in old_files}
        directories |= {os.path.dirname(p) for p in self.new_directory_files}
        directories &= loaded_as_module
        directories -= self._module_file_set_handled(parsed, removed, directories, old_files)
        return {unit_of_key(k) for k in self.pickled_definitions
                if k.tf_source_modules and os.path.dirname(k.file_path) in directories}

    def _module_file_set_handled(self, parsed: dict[TFDefinitionKey, Any], removed: set[TFDefinitionKey],
                                 directories: set[str], old_files: set[str]) -> set[str]:
        """Round 9 step 1b (module_files.py): directories whose single added / deleted LAST file is handled per
        module instance; their callers' `__resolved__` lists are patched into `parsed` (callers become changed keys,
        recreated by the per-owner path) instead of re-parsing every calling unit."""
        if not directories:
            self.module_file_set_report = {"handled": [], "refused": {}}
            return set()
        added = {k.file_path: d for k, d in parsed.items() if k.tf_source_modules and k.file_path not in old_files}
        deleted = {k.file_path for k in removed if k.tf_source_modules}
        plan = ModuleFileSetPlan(self.pickled_definitions, self.a["files"], loads)
        handled = plan.decide(directories, added, deleted)
        self.module_file_set_report = {"handled": sorted(os.path.relpath(d, self.root) for d in handled),
                                       "refused": {os.path.relpath(d, self.root): r for d, r in plan.refused.items()}}
        if not handled:
            return set()
        handled_added = {p for p in added if os.path.dirname(p) in handled}
        handled_deleted = {p for p in deleted if os.path.dirname(p) in handled}
        patches = plan.caller_patches(handled_added, handled_deleted)
        self.resolved_patches = {
            (key.file_path, key.tf_source_modules, name): data.get(RESOLVED_MODULE_ENTRY_NAME)
            for key in patches for name, data in _module_calls(loads(self.pickled_definitions[key])).items()}
        for key, definition in patches.items():
            parsed[key] = parsed[key] if key in parsed else definition
            if key in parsed and parsed[key] is not definition:
                parsed[key] = self._merge_resolved(parsed[key], definition)
        return handled

    @staticmethod
    def _merge_resolved(edited: dict[str, Any], patched: dict[str, Any]) -> dict[str, Any]:
        """A caller file edited by the PR AND calling a handled directory: keep the PR's content, take the patched
        `__resolved__` of calls whose target did not change."""
        patched_calls = _module_calls(patched)
        for name, data in _module_calls(edited).items():
            if name in patched_calls and _call_signature(data) == _call_signature(patched_calls[name]):
                data[RESOLVED_MODULE_ENTRY_NAME] = patched_calls[name].get(RESOLVED_MODULE_ENTRY_NAME)
        return edited

    def _pr_local_call_targets(self, parsed: dict[TFDefinitionKey, Any],
                               removed: set[TFDefinitionKey]) -> tuple[dict[str, set[str]], set[str]]:
        gone = {k.file_path for k in removed} | set(self.changes.deleted)
        parsed_files = {k.file_path: d for k, d in parsed.items()}
        parsed_files.update(self.new_directory_files)
        pr_files: set[str] = set(parsed_files)
        targets: dict[str, set[str]] = defaultdict(set)
        seen_unchanged: set[str] = set()
        for key, entry in self.definition_entries.items():
            fp = key.file_path
            if fp in gone or fp in parsed_files or fp in seen_unchanged:
                continue
            seen_unchanged.add(fp)
            pr_files.add(fp)
            if not is_external_module_path(fp, self.root):
                f_dir = os.path.dirname(fp)
                if "local_sources" in entry:
                    for src in entry["local_sources"]:
                        targets[f_dir].add(os.path.normpath(os.path.join(f_dir, src)))
                else:
                    for data in _module_calls(loads(entry["definition"])).values():
                        src = (data.get("source") or [None])[0]
                        if isinstance(src, str) and src.startswith(("./", "../")):
                            targets[f_dir].add(os.path.normpath(os.path.join(f_dir, src)))
        for fp, d in parsed_files.items():
            if not is_external_module_path(fp, self.root):
                f_dir = os.path.dirname(fp)
                for data in _module_calls(d).values():
                    src = (data.get("source") or [None])[0]
                    if isinstance(src, str) and src.startswith(("./", "../")):
                        targets[f_dir].add(os.path.normpath(os.path.join(f_dir, src)))
        return targets, pr_files

    def _reparse_reasons(self, parsed: dict[TFDefinitionKey, Any], removed: set[TFDefinitionKey],
                         module_fields: dict[str, Any]) -> dict[str, str]:
        """unit directory -> why its definition keys must be re-derived by a unit re-parse."""
        reasons: dict[str, str] = {}
        topology_changed = self._topology_changed_units(parsed, removed)
        for unit in topology_changed:
            reasons[unit] = "module call added/removed/re-sourced"
        if NEGATIVE_CONTROL != "no_module_fileset_rule":
            for unit in self._module_file_set_changed_units(parsed, removed):
                reasons.setdefault(unit, "file set of a loaded module directory changed (__resolved__ lists files)")
        if topology_changed or self.new_directory_files or removed:
            kinds = self._baseline_directories()
            targets_map, pr_files = self._pr_local_call_targets(parsed, removed)
            pr_called = {t for ts in targets_map.values() for t in ts}
            for path in self.new_directory_files:
                directory = os.path.dirname(path)
                if directory in pr_called:
                    callers = [k for k in self.pickled_definitions if os.path.dirname(k.file_path) == directory]
                    if not callers:
                        reasons.update({unit_of_key(TFDefinitionKey(p)): "new local module directory called"
                                        for p in pr_files
                                        if directory in targets_map.get(os.path.dirname(p), set())})
                else:
                    reasons[directory] = "new root directory"
            for directory, kind in kinds.items():
                if is_external_module_path(directory, self.root):
                    continue
                now_called = directory in pr_called
                if kind == "unit" and now_called:
                    reasons[directory] = "root directory became a called module"
                if kind == "module" and not now_called and any(os.path.dirname(p) == directory for p in pr_files):
                    reasons[directory] = "module directory no longer called (becomes a root unit)"
        reasons.update(self._external_module_changes())
        if self._variable_inputs_changed() and NEGATIVE_CONTROL != "ignore_variable_inputs":
            scratch = os.path.join(os.path.dirname(self.root), ".dfo_scratch", "tfvars")
            self.new_tfvar_blocks = self._recompute_tfvar_blocks(scratch, module_fields)
        if NEGATIVE_CONTROL == "no_reparse":
            return {}
        return reasons

    def _external_module_changes(self) -> dict[str, str]:
        """Units that load an external module whose content differs from the baseline's (version bump in the repo is
        handled as a call re-source; this covers upstream content changes for the SAME address). The baseline
        stores each external module file's content in `files`; the PR's materialised copy is compared to it."""
        reasons: dict[str, str] = {}
        materialized = os.path.join(self.root, ".external_modules")
        if not os.path.isdir(materialized) and not self.a["variable_inputs"].get("external_modules"):
            self.external_files = {}
            return reasons
        stored = {p: lines for p, lines in self.a["files"].items() if is_external_module_path(p, self.root)}
        current: dict[str, list[str]] = {}
        for directory, _, names in os.walk(materialized):
            for name in names:
                if is_terraform_file(name):
                    path = os.path.join(directory, name)
                    with open(path) as f:
                        current[path] = f.readlines()
        changed_files = {p for p in set(stored) | set(current) if stored.get(p) != current.get(p)}
        if NEGATIVE_CONTROL == "no_external_change_detection":
            changed_files = set()
        changed_dirs = {os.path.dirname(p) for p in changed_files}
        for key in self.pickled_definitions:
            if os.path.dirname(key.file_path) in changed_dirs:
                reasons[unit_of_key(key)] = "external module content changed upstream"
        self.external_files = current
        return reasons

    def _unit_module_dirs(self, unit: str, targets: dict[str, set[str]]) -> tuple[set[str], set[str]]:
        """(local module directories reachable from the unit, external module directories it uses)."""
        reachable: set[str] = set()
        pending = [unit]
        while pending:
            directory = pending.pop()
            for target in targets.get(directory, set()):
                if target not in reachable and target != unit:
                    reachable.add(target)
                    pending.append(target)
        return reachable, set()

    def _reparsed_unit_definitions(self, unit: str, targets: dict[str, set[str]], files: dict[str, list[str]],
                                   pr_units: set[str]) -> tuple[dict[TFDefinitionKey, Any], dict[str, Any]]:
        module_dirs, _ = self._unit_module_dirs(unit, targets)
        files = {p: lines for p, lines in files.items() if not is_external_module_path(p, self.root)}
        excluded = sorted(u for u in pr_units if u != unit and u.startswith(unit + os.sep))
        excluded += sorted(d for d in {os.path.dirname(p) for p in files}
                           if d.startswith(unit + os.sep) and d not in module_dirs and d not in excluded)
        scratch = os.path.join(os.path.dirname(self.root), ".dfo_scratch", "units",
                               os.path.relpath(unit, self.root).replace(os.sep, "__"))
        tree = VirtualTree(scratch, self.root, files)
        definitions, parser_state = parse_unit(unit, tree, module_dirs, excluded, external_modules(self.root),
                                               var_files_from_env(self.root))
        definitions = {k: v for k, v in definitions.items() if unit_of_key(k) == unit}
        self.extra_source_map.update(parser_state["external_modules_source_map"])
        return definitions, parser_state["external_vars"]

    def _build_with_reparsed_units(self, parsed: dict[TFDefinitionKey, Any], changed: set[TFDefinitionKey],
                                   removed: set[TFDefinitionKey], module_fields: dict[str, Any],
                                   reasons: dict[str, str]) -> TerraformLocalGraph:
        """Every unit named in `reasons` is re-parsed (Checkov's parser, virtual tree) and rebuilt (Checkov's
        pre-render pipeline). Other changed units go through the regular scoped / per-owner paths."""
        targets, _ = self._pr_local_call_targets(parsed, removed)
        pr_called = {t for ts in targets.values() for t in ts}
        kinds = self._baseline_directories()
        pr_units = {u for u, k in kinds.items() if k == "unit"} | {os.path.dirname(p) for p in self.new_directory_files}
        pr_units = {u for u in pr_units if u not in pr_called} | {u for u in reasons}
        all_needed_dirs: set[str] = set()
        for unit in reasons:
            m_dirs, _ = self._unit_module_dirs(unit, targets)
            all_needed_dirs.add(unit)
            all_needed_dirs |= m_dirs
        files = {
            p: lines for p, lines in self.a["files"].items()
            if os.path.dirname(p) in all_needed_dirs or any(os.path.dirname(p).startswith(u + os.sep) for u in reasons)
        }
        for path in self.changes.deleted:
            files.pop(path, None)
        for path in self.changes.changed:
            if not is_variable_file(path) and (
                os.path.dirname(path) in all_needed_dirs
                or any(os.path.dirname(path).startswith(u + os.sep) for u in reasons)
            ):
                with open(path) as f:
                    files[path] = f.readlines()
        variable_files = dict(self.a["variable_inputs"]["files"])
        for path in self.changes.deleted:
            variable_files.pop(path, None)
        for path in self.changes.changed:
            if is_variable_file(path):
                with open(path, encoding="utf-8-sig") as f:
                    variable_files[path] = f.read()
        files.update({p: t.splitlines(keepends=True) for p, t in variable_files.items()})
        reparsed: dict[str, dict[TFDefinitionKey, Any]] = {}
        tfvars_by_unit: dict[str, list[Any]] = {}
        new_tfvars = getattr(self, "new_tfvar_blocks", None)
        for unit in sorted(reasons):
            definitions, external_vars = self._reparsed_unit_definitions(unit, targets, files, pr_units)
            reparsed[unit] = definitions
            if new_tfvars is not None:
                tfvars_by_unit[unit] = [b for b in new_tfvars if str(b.attributes.get("load_dir")) in
                                        {os.path.dirname(k.file_path) for k in definitions} | {unit}]
            else:
                tfvars_by_unit[unit] = tfvar_blocks(external_vars, module_fields["source"])
        self.reparsed_units = {u: {"reason": reasons[u], "definition_keys": len(reparsed[u]),
                                   "files_from_artifact": len({k.file_path for k in reparsed[u]}
                                                              - set(self.changes.changed))}
                               for u in reparsed}
        reparse_parsed = {k: v for definitions in reparsed.values() for k, v in definitions.items()}
        rest_parsed = {k: v for k, v in parsed.items() if unit_of_key(k) not in reasons}
        rest_changed = {k for k in changed if unit_of_key(k) not in reasons}
        rest_removed = {k for k in removed if unit_of_key(k) not in reasons}
        self._reparsed = (reparsed, tfvars_by_unit)
        all_parsed = {**rest_parsed, **reparse_parsed}
        removed_for_assembly = rest_removed | {k for k in self.pickled_definitions if unit_of_key(k) in reasons}
        removed_for_assembly -= set(reparse_parsed)
        scoped = self._scoped_units(rest_parsed, rest_changed, rest_removed)
        unit_fields = {**module_fields, "external_modules_source_map": {**module_fields["external_modules_source_map"],
                                                                        **self.extra_source_map}}
        return self._build_with_scoped_units(all_parsed, rest_changed | set(reparse_parsed), removed_for_assembly,
                                             unit_fields, scoped, reparsed_units=set(reasons))

    # ------------------------------------------------------------------------------------------- count / for_each

    def _scoped_units(self, parsed: dict[TFDefinitionKey, Any], changed: set[TFDefinitionKey],
                      removed: set[TFDefinitionKey]) -> set[str]:
        """Units that must be rebuilt with Checkov's own pipeline (ForeachBuilder).

        When resource-level units are enabled (default: CHECKOV_DIFF_RESOURCE_LEVEL_UNITS=true):
          A unit needs a whole-unit scoped rebuild ONLY IF:
          1. A file containing count or for_each blocks was added, modified, or removed in that unit, OR
          2. A variable, local, or resource that transitively feeds a `count` or `for_each` attribute was modified.
          Units whose count/for_each constructs are unaffected are updated at resource level (per-owner),
          reusing their baseline-expanded instances and skipping sub-graph rendering entirely.

        When off or under negative control `no_resource_level_units`:
          Any changed unit that contained count/for_each at baseline gets a whole-unit scoped rebuild."""
        if os.getenv("CHECKOV_DIFF_RESOURCE_LEVEL_UNITS", "true").lower() != "true" or NEGATIVE_CONTROL == "no_resource_level_units":
            units: set[str] = set()
            for key in changed | removed:
                unit = unit_of_key(key)
                before = self.a["units"].get(unit, {}).get("has_foreach", False)
                after = key in parsed and has_count_or_foreach(parsed[key])
                if before or after:
                    units.add(unit)
            return units

        scoped: set[str] = set()
        for key in changed | removed:
            unit = unit_of_key(key)
            entry = self.definition_entries.get(key)
            before = entry["has_foreach"] if entry and "has_foreach" in entry \
                else (key in self.pickled_definitions and has_count_or_foreach(loads(self.pickled_definitions[key])))
            after = key in parsed and has_count_or_foreach(parsed[key])
            if before or after:
                scoped.add(unit)

        module_fields = loads(self.a["module"])
        truly_changed_vertices: set[int] = set()
        if changed:
            cand_indices = {i for k in changed if k in self.definition_entries for i in self.definition_entries[k]["vertices"]}
            keys_sec = self.old_keys or self.a["keys"]
            cand_old_index = {keys_sec[i]: i for i in cand_indices}
            cd_sec = self.a["creation_digests"]
            self._scoped_changed_digests = {i: cd_sec[i] for i in cand_indices}
            for key in changed:
                blocks = self._create_blocks(key, parsed[key], module_fields["source"],
                                             module_fields["external_modules_source_map"], module_fields["source_dir"])
                for block in blocks:
                    vk = lookups_vertex_key(block, self.root)
                    old_idx = cand_old_index.get(vk)
                    if old_idx is None and self.old_index:
                        old_idx = self.old_index.get(vk)
                    if old_idx is None or self._scoped_changed_digests.get(old_idx) != creation_digest(block, self.root):
                        if old_idx is not None:
                            truly_changed_vertices.add(old_idx)
                        if block.block_type in FOREACH_BLOCK_TYPES and (
                                FOREACH_STRING in block.attributes or COUNT_STRING in block.attributes):
                            scoped.add(unit_of_key(key))
            del cd_sec, keys_sec
        else:
            self._scoped_changed_digests = {}
        if hasattr(self.a, "release"):
            self.a.release("creation_digests")
        for key in removed:
            entry = self.definition_entries.get(key)
            if entry:
                truly_changed_vertices.update(entry["vertices"])

        if getattr(self, "new_tfvar_blocks", None) is not None:
            truly_changed_vertices.update(self.a.get("tfvar_vertices", []))

        unit_by_v = self.a["unit_by_vertex"]
        old_by_u: dict[str, list[int]] = defaultdict(list)
        for idx, u_str in enumerate(unit_by_v):
            old_by_u[u_str].append(idx)
        self._old_by_unit = old_by_u
        if hasattr(self.a, "release"):
            self.a.release("unit_by_vertex")

        truly_changed_units = {unit_by_v[i] for i in truly_changed_vertices}
        referrers: dict[int, list[tuple[int, str]]] = defaultdict(list)
        if truly_changed_vertices and NEGATIVE_CONTROL != "ignore_count_dependencies":
            for origin, dest, label, _, _ in self.a["edges"]:
                if unit_by_v[origin] in truly_changed_units:
                    referrers[dest].append((origin, label))
            if hasattr(self.a, "release"):
                self.a.release("edges")

        stack = list(truly_changed_vertices)
        visited = set(truly_changed_vertices)
        while stack:
            curr = stack.pop()
            for origin, label in referrers.get(curr, []):
                if label in ("count", "for_each"):
                    scoped.add(unit_by_v[origin])
                if origin not in visited:
                    visited.add(origin)
                    stack.append(origin)
        del unit_by_v
        return scoped

    def _unit_artifact(self, unit: str) -> dict[str, Any]:
        """The artifact restricted to one unit (no count/for_each in it): vertex lists, edges, probes re-indexed."""
        old_by_unit = getattr(self, "_old_by_unit", None)
        members = list(old_by_unit[unit]) if old_by_unit is not None else [
            i for i, u in enumerate(self.a["unit_by_vertex"]) if u == unit
        ]
        position = {old: new for new, old in enumerate(members)}
        if self._defs_by_unit is None:
            by_u: dict[str, list[tuple[TFDefinitionKey, Any]]] = defaultdict(list)
            for k, entry in self.definition_entries.items():
                by_u[unit_of_key(k)].append((k, entry))
            self._defs_by_unit = by_u
        pre_keyed: dict[TFDefinitionKey, Any] = {}
        definitions = []
        for k, entry in self._defs_by_unit.get(unit, ()):
            new_verts = [position[i] for i in entry["vertices"]]
            new_entry = entry.with_vertices(new_verts) if hasattr(entry, "with_vertices") \
                else {**entry, "vertices": new_verts}
            pre_keyed[k] = new_entry
            definitions.append(new_entry)
        class _SubSlice:
            def __init__(self, base_seq: Any, indices: list[int]) -> None:
                self._base = base_seq
                self._indices = indices
            def __getitem__(self, i: int) -> Any:
                return self._base[self._indices[i]]
            def __len__(self) -> int:
                return len(self._indices)
            def __iter__(self) -> Iterator[Any]:
                return (self._base[idx] for idx in self._indices)

        edges_by_unit = getattr(self, "_edges_by_unit", None)
        if edges_by_unit is not None:
            raw_unit_edges = edges_by_unit.get(unit, [])
        else:
            raw_unit_edges = [row for row in self.a["edges"] if row[0] in position]
        sm_unit_map = getattr(self, "_sm_by_unit", {})
        mc_unit_map = getattr(self, "_mc_by_unit", {})
        cd_unit_map = getattr(self, "_cd_by_unit", {})
        fp_unit_map = getattr(self, "_fp_by_unit", {})
        probes_unit_map = getattr(self, "_probes_by_unit", {})
        sm_unit = sm_unit_map[unit] if unit in sm_unit_map else [self.a["source_module"][i] for i in members]
        mc_unit = mc_unit_map[unit] if unit in mc_unit_map else [self.a["module_connections"][i] for i in members]
        cd_unit_raw = cd_unit_map[unit] if unit in cd_unit_map else [self.a["creation_digests"][i] for i in members]
        cd_unit = [cd_unit_raw.get(old_i, "") for old_i in members] if isinstance(cd_unit_raw, dict) else cd_unit_raw
        fp_unit = fp_unit_map[unit] if unit in fp_unit_map else [self.a["fingerprints"][i] for i in members]
        probes_unit = probes_unit_map[unit] if unit in probes_unit_map else {
            str(new_i): self.a["probes"][str(old_i)] for new_i, old_i in enumerate(members)
            if str(old_i) in self.a["probes"]
        }
        keys_unit_map = getattr(self, "_keys_by_unit", {})
        keys_unit = keys_unit_map[unit] if unit in keys_unit_map else [self.a["keys"][i] for i in members]
        return _ArtifactOverlay(self.a, {
            "keys": keys_unit,
            "vertices": _SubSlice(self.a["vertices"], members),
            "creation_digests": cd_unit,
            "fingerprints": fp_unit,
            "source_module": [[position[j] for j in sm_row if j in position] for sm_row in sm_unit],
            "module_connections": mc_unit,
            "tfvar_vertices": [position[i] for i in self.a["tfvar_vertices"] if i in position],
            "edges": [[position[o], position[d], label, position[w], phase]
                      for o, d, label, w, phase in raw_unit_edges],
            "probes": probes_unit,
            "definitions": definitions,
            "pre_keyed_definitions": pre_keyed,
            "foreach_ran": False,
            "global_positions": members,
        })

    def _per_owner_unit(self, unit: str, parsed: dict[TFDefinitionKey, Any], changed: set[TFDefinitionKey],
                        removed: set[TFDefinitionKey], module_fields: dict[str, Any]) -> "_UnitResult":
        sub = DiffEngine.__new__(DiffEngine)
        sub.__init__(self._unit_artifact(unit), self.root, self.changes)
        pr_t, pr_a = self._pr_global_tokens(parsed, removed)
        if getattr(self, "_cached_old_types", None) is None:
            self._cached_old_types = {t for d in self.definition_entries.values() for t in d["resource_types"]}
        sub._cached_old_types = self._cached_old_types
        sub._global_parsed_and_removed = (parsed, removed, self.definition_entries, self.a["aliases"],
                                          self.a["alias_keys"], pr_t, pr_a)
        if getattr(self, "new_tfvar_blocks", None) is not None:
            sub.unit_tfvar_blocks = self._unit_tfvar_blocks(unit)
        unit_parsed = {k: v for k, v in parsed.items() if unit_of_key(k) == unit}
        unit_changed = {k for k in changed if unit_of_key(k) == unit}
        unit_removed = {k for k in removed if unit_of_key(k) == unit}
        vertices, fresh = sub._splice_vertices(unit_parsed, unit_changed, unit_removed, module_fields)
        graph = sub._per_owner_graph(vertices, fresh, unit_parsed, unit_changed, unit_removed, module_fields)
        sub.release_pre_render_state()
        return _UnitResult(graph, sub.report, sub)

    def _unit_keys(self, unit: str) -> list[TFDefinitionKey]:
        """Baseline definition keys of `unit`, in definition_entries order (grouped once for all units)."""
        if self._defs_by_unit is None:
            by_u: dict[str, list[tuple[TFDefinitionKey, Any]]] = defaultdict(list)
            for k, entry in self.definition_entries.items():
                by_u[unit_of_key(k)].append((k, entry))
            self._defs_by_unit = by_u
        return [k for k, _ in self._defs_by_unit.get(unit, ())]

    def _unit_definitions(self, unit: str, parsed: dict[TFDefinitionKey, Any],
                          removed: set[TFDefinitionKey]) -> dict[TFDefinitionKey, Any]:
        definitions = {k: loads(self.pickled_definitions[k]) for k in self._unit_keys(unit)
                       if k not in removed and k not in parsed}
        definitions.update({k: v for k, v in parsed.items() if unit_of_key(k) == unit})
        return definitions

    def _tfvar_source(self) -> list[Any]:
        new_blocks = getattr(self, "new_tfvar_blocks", None)
        return new_blocks if new_blocks is not None else [loads(t) for t in self.a["tfvar_blocks"]]

    def _tfvar_units(self) -> dict[tuple[str, str], str]:
        """(load_dir, name) -> unit the baseline placed that tfvar vertex in (the unit of the variable it feeds)."""
        placement: dict[tuple[str, str], str] = {}
        old_by_u = getattr(self, "_old_by_unit", None)
        u_of_idx = {i: u for u, idxs in old_by_u.items() for i in idxs} if old_by_u is not None else None
        for index in self.a["tfvar_vertices"]:
            block = self._reused_vertex(index)
            u_str = u_of_idx[index] if u_of_idx is not None else self.a["unit_by_vertex"][index]
            placement[(str(block.attributes.get("load_dir")), block.name)] = u_str
        return placement

    def _tfvar_unit(self, block: Any) -> str:
        """Unit of a (possibly new) tfvar block. A tfvar for a directory loaded by several units feeds the FIRST
        variable of its name in that directory in Checkov's global order: only the baseline placement says which.
        A tfvar not present at baseline for a directory loaded by more than one unit cannot be placed: unsupported."""
        load_dir = str(block.attributes.get("load_dir"))
        placed = self._tfvar_units().get((load_dir, block.name))
        if placed is not None:
            return placed
        units = {unit_of_key(k) for k in self.pickled_definitions if os.path.dirname(k.file_path) == load_dir}
        if len(units) > 1:
            raise IncrementalGraphUnsupported(
                f"new tfvar {block.name} for {os.path.relpath(load_dir, self.root)}, a directory loaded by "
                f"{len(units)} units: Checkov feeds the first instance in global vertex order")
        return next(iter(units)) if units else load_dir

    def _unit_tfvar_blocks(self, unit: str) -> list[Any]:
        """The tfvar blocks a unit's graph holds (pre-pipeline), with the PR's variable inputs when they changed."""
        return [b for b in self._tfvar_source() if self._tfvar_unit(b) == unit]

    def _tfvar_changed_units(self) -> set[str]:
        """Units whose tfvar vertices change with the PR's variable inputs (empty when inputs did not change)."""
        new_blocks = getattr(self, "new_tfvar_blocks", None)
        if new_blocks is None:
            return set()
        old_blocks = [loads(t) for t in self.a["tfvar_blocks"]]
        signature = lambda b: (b.name, json.dumps(b.attributes, sort_keys=True, default=str), str(b.path))  # noqa: E731
        old_by_unit: dict[str, set[Any]] = defaultdict(set)
        new_by_unit: dict[str, set[Any]] = defaultdict(set)
        for block in old_blocks:
            old_by_unit[self._tfvar_unit(block)].add(signature(block))
        for block in new_blocks:
            new_by_unit[self._tfvar_unit(block)].add(signature(block))
        return {u for u in set(old_by_unit) | set(new_by_unit) if old_by_unit[u] != new_by_unit[u]}

    def _build_with_scoped_units(self, parsed: dict[TFDefinitionKey, Any], changed: set[TFDefinitionKey],
                                 removed: set[TFDefinitionKey], module_fields: dict[str, Any],
                                 scoped: set[str], reparsed_units: frozenset[str] | set[str] = frozenset()) \
            -> TerraformLocalGraph:
        """Graph = (unchanged units, spliced verbatim) + (changed units without count/for_each, per-owner engine on the
        unit) + (scoped units: changed with count/for_each, rebuilt by Checkov's own pipeline on the unit only).

        Unchanged units keep vertices, edges in baseline order and their accumulated index fields, all remapped.
        Rendering is independent of vertex and edge order (order_experiment.py), so units can be concatenated."""
        scoped = set(scoped) | set(reparsed_units)
        tfvar_changed = self._tfvar_changed_units() - scoped
        scoped |= {u for u in tfvar_changed if self.a["units"].get(u, {}).get("has_foreach")}
        token_units = self._units_reading_changed_tokens(parsed, removed) - scoped
        scoped |= {u for u in token_units if self.a["units"].get(u, {}).get("has_foreach")}
        self.token_units = token_units
        per_owner = ({unit_of_key(k) for k in changed | removed} | tfvar_changed | token_units) - scoped
        if NEGATIVE_CONTROL != "per_owner_module_expansion":
            # The per-owner path splices definition keys in sorted order and has no per-instance expansion: a unit
            # holding a module count / for_each anywhere in its tree (the call may sit in a nested module file) would
            # lose the expanded instances. Such units go to the scoped path (instance-level or rebuild).
            expanded = {u for u in per_owner if self.a["units"].get(u, {}).get("has_module_foreach")}
            scoped |= expanded
            per_owner -= expanded
        self.touched_units = per_owner | scoped
        old_by_unit = getattr(self, "_old_by_unit", None)
        if old_by_unit is None:
            old_by_unit = defaultdict(list)
            for index, unit in enumerate(self.a["unit_by_vertex"]):
                old_by_unit[unit].append(index)
            self._old_by_unit = old_by_unit
        scd = getattr(self, "_scoped_changed_digests", None)
        if scd is not None and all(
            old_i in scd
            for u in per_owner | scoped
            for k, entry in (self._defs_by_unit or {}).get(u, [
                (k2, e2) for k2, e2 in self.definition_entries.items() if unit_of_key(k2) == u
            ])
            if k in changed
            for old_i in entry["vertices"]
        ) and not self._tfvar_changed_units():
            self._scoped_cd_cache = {u: {old_i: scd[old_i] for old_i in old_by_unit[u] if old_i in scd}
                                     for u in per_owner | scoped}
        else:
            self._scoped_cd_cache = {u: [self.a["creation_digests"][i] for i in old_by_unit[u]] for u in per_owner | scoped}
            if hasattr(self.a, "release"):
                self.a.release("creation_digests")
        if hasattr(self.a, "release"):
            self.a.release("unit_by_vertex")
        self._total_units_count = len(self.a["units"]) if "units" in self.a else 0
        self._unit_names_set = set(self.a["units"]) if "units" in self.a else set()
        if hasattr(self.a, "release"):
            self.a.release("units")
        keys_sec_for_build = self.old_keys or self.a["keys"]
        self.old_keys = keys_sec_for_build
        self._keys_by_unit = {u: [keys_sec_for_build[i] for i in old_by_unit[u]] for u in per_owner | scoped}
        self._old_keys_count = len(keys_sec_for_build)
        self.old_index = {}
        import array
        vertices: list[Any] = []
        new_index_of_old = array.array("i", [-1]) * self._old_keys_count
        self._is_splicing_unchanged = True
        for unit in sorted(old_by_unit):
            if unit in scoped or unit in per_owner:
                continue
            for old in old_by_unit[unit]:
                new_index_of_old[old] = len(vertices)
                vertices.append(self._reused_vertex(old))
        self._is_splicing_unchanged = False
        del keys_sec_for_build
        if hasattr(self.a, "release"):
            self.old_keys = []
            self.a.release("keys")
        import gc
        gc.collect()
        sm_sec = self.a["source_module"]
        for old, new in enumerate(new_index_of_old):
            if new < 0:
                continue
            vertex = vertices[new]
            sm_old = sm_sec[old]
            vertex.source_module = {new_index_of_old[i] for i in sm_old} if sm_old else set()
            if isinstance(vertex, LazyTerraformBlock):
                vertex.dfo_baseline_sm_indices = vertex.source_module
                vertex.dfo_baseline_source_module = None
            if NEGATIVE_CONTROL == "no_index_field_restore":
                vertex.source_module = set()
        self._sm_by_unit = {u: [sm_sec[i] for i in old_by_unit[u]] for u in per_owner | scoped}
        del sm_sec
        if hasattr(self.a, "release"):
            self.a.release("source_module")
        mc_sec = self.a["module_connections"]
        for old, new in enumerate(new_index_of_old):
            if new < 0:
                continue
            vertex = vertices[new]
            mc_old = mc_sec[old]
            vertex.module_connections = {attr: [new_index_of_old[i] for i in ids]
                                         for attr, ids in mc_old.items()} if mc_old else {}
            if NEGATIVE_CONTROL == "no_index_field_restore":
                vertex.module_connections = {}
        self._mc_by_unit = {u: [mc_sec[i] for i in old_by_unit[u]] for u in per_owner | scoped}
        del mc_sec
        if hasattr(self.a, "release"):
            self.a.release("module_connections")
        edges: list[tuple[int, int, str]] = []
        edges_by_unit: dict[str, list[list[Any]]] = defaultdict(list)
        unit_of_old = {old_i: u for u in per_owner | scoped for old_i in old_by_unit[u]}
        raw_edges_sec = self.a["edges"]
        self._baseline_edge_count = len(raw_edges_sec)
        for edge_row in raw_edges_sec:
            origin = edge_row[0]
            new_o = new_index_of_old[origin]
            if new_o >= 0:
                edges.append((new_o, new_index_of_old[edge_row[1]], edge_row[2]))
            elif origin in unit_of_old:
                edges_by_unit[unit_of_old[origin]].append(edge_row)
        del unit_of_old, raw_edges_sec, new_index_of_old
        self._edges_by_unit = edges_by_unit
        if hasattr(self.a, "release"):
            self.a.release("edges")
        self._cd_by_unit = self._scoped_cd_cache
        fp_sec = self.a["fingerprints"]
        self._fp_by_unit = {u: [fp_sec[i] for i in old_by_unit[u]] for u in per_owner | scoped}
        del fp_sec
        if hasattr(self.a, "release"):
            self.a.release("fingerprints")
        probes_sec = self.a["probes"]
        self._probes_by_unit = {
            u: {str(new_i): probes_sec[str(old_i)] for new_i, old_i in enumerate(old_by_unit[u]) if str(old_i) in probes_sec}
            for u in per_owner | scoped
        }
        del probes_sec
        if hasattr(self.a, "release"):
            self.a.release("probes")
        gc.collect()
        reused_vertices, reused_edges = len(vertices), len(edges)
        unit_reports: dict[str, Any] = {}
        for unit in sorted(per_owner):
            sub = self._per_owner_unit(unit, parsed, changed, removed, module_fields)
            if not getattr(sub.engine, "_edge_tuples_identical_to_baseline", True):
                self._edge_tuples_identical_to_baseline = False
            offset = len(vertices)
            vertices.extend(sub.graph.vertices)
            for vertex in sub.graph.vertices:
                vertex.source_module = {i + offset for i in vertex.source_module}
                if isinstance(getattr(vertex, "dfo_baseline_sm_indices", None), set):
                    vertex.dfo_baseline_sm_indices = {i + offset for i in vertex.dfo_baseline_sm_indices}
                vertex.module_connections = {a: [i + offset for i in ids] for a, ids in vertex.module_connections.items()}
            edges.extend((e.origin + offset, e.dest + offset, e.label) for e in sub.graph.edges)
            if not hasattr(self, "_rebuilt_unit_offsets"):
                self._rebuilt_unit_offsets: dict[str, tuple[int, int]] = {}
            self._rebuilt_unit_offsets[unit] = (offset, len(vertices))
            reused_vertices += sub.report.vertices_reused
            reused_edges += sub.report.edges_reused
            unit_reports[unit] = {"mode": "per-owner", "vertices": sub.report.vertices,
                                  "vertices_rebuilt": sub.report.vertices_rebuilt, "edges": sub.report.edges,
                                  "edges_rebuilt": sub.report.edges_rebuilt,
                                  "edge_owners_rebuilt": sub.report.edge_owners_rebuilt}
        for unit in sorted(scoped):
            if not any(unit_of_key(k) == unit for k in self.definition_entries if k not in removed) \
                    and not any(unit_of_key(k) == unit for k in parsed) and not self._unit_tfvar_blocks(unit):
                unit_reports[unit] = {"mode": "deleted", "deleted": True}
                continue
            global_types, global_aliases = self._pr_global_tokens(parsed, removed)
            oracle = self._expansion_oracle()
            if unit not in reparsed_units and oracle is not None and instance_update_enabled() \
                    and NEGATIVE_CONTROL != "stale_scoped_unit":
                instance_result = self._instance_level_unit(unit, parsed, changed, removed, module_fields,
                                                            global_types, global_aliases)
                if instance_result is not None:
                    sub, report = instance_result
                    if not getattr(sub.engine, "_edge_tuples_identical_to_baseline", True):
                        self._edge_tuples_identical_to_baseline = False
                    offset = len(vertices)
                    vertices.extend(sub.graph.vertices)
                    for vertex in sub.graph.vertices:
                        vertex.source_module = {i + offset for i in vertex.source_module}
                        if isinstance(getattr(vertex, "dfo_baseline_sm_indices", None), set):
                            vertex.dfo_baseline_sm_indices = {i + offset for i in vertex.dfo_baseline_sm_indices}
                        vertex.module_connections = {a: [i + offset for i in ids]
                                                     for a, ids in vertex.module_connections.items()}
                    edges.extend((e.origin + offset, e.dest + offset, e.label) for e in sub.graph.edges)
                    if not hasattr(self, "_rebuilt_unit_offsets"):
                        self._rebuilt_unit_offsets = {}
                    self._rebuilt_unit_offsets[unit] = (offset, len(vertices))
                    reused_vertices += sub.report.vertices_reused
                    reused_edges += sub.report.edges_reused
                    unit_reports[unit] = report
                    continue
            if unit in reparsed_units:
                definitions = self._reparsed[0][unit]
                tfvars = self._reparsed[1][unit]
            else:
                definitions = self._unit_definitions(unit, parsed, removed)
                tfvars = self._unit_tfvar_blocks(unit)
            if not definitions and not tfvars:
                unit_reports[unit] = {"mode": "deleted", "deleted": True}
                continue
            if NEGATIVE_CONTROL == "stale_scoped_unit":
                definitions = {k: loads(v) for k, v in self.pickled_definitions.items() if unit_of_key(k) == unit}
            if NEGATIVE_CONTROL == "unit_local_lookups":
                unit_graph, _ = build_unit(definitions, tfvars, module_fields, self.root, statement_oracle=oracle)
            else:
                unit_graph, _ = build_unit(definitions, tfvars, module_fields, self.root,
                                           global_resource_types=global_types,
                                           global_aliases={n: {"block_type_": b} for n, b in global_aliases},
                                           statement_oracle=oracle)
            offset = len(vertices)
            vertices.extend(unit_graph.vertices)
            for vertex in unit_graph.vertices:
                vertex.source_module = {i + offset for i in vertex.source_module}
                vertex.module_connections = {a: [i + offset for i in ids] for a, ids in vertex.module_connections.items()}
            edges.extend((e.origin + offset, e.dest + offset, e.label) for e in unit_graph.edges)
            if not hasattr(self, "_rebuilt_unit_offsets"):
                self._rebuilt_unit_offsets: dict[str, tuple[int, int]] = {}
            self._rebuilt_unit_offsets[unit] = (offset, len(vertices))
            mode = "reparse+rebuild" if unit in reparsed_units else "scoped-rebuild"
            unit_reports[unit] = {"mode": mode,
                                  "reason": getattr(self, "reparsed_units", {}).get(unit, {}).get("reason"),
                                  "vertices": len(unit_graph.vertices),
                                  "vertices_rebuilt": len(unit_graph.vertices), "edges": len(unit_graph.edges),
                                  "edges_rebuilt": len(unit_graph.edges),
                                  "definition_keys": len(definitions),
                                  "definition_keys_from_artifact": len(definitions) - len(
                                      [k for k in definitions if k in parsed]),
                                  "foreach_expanded": any(unit_graph.foreach_blocks.values()),
                                  **self._expansion_report(oracle)}
        graph = self._assemble(vertices, edges, parsed, removed, changed, module_fields)
        self._last_parsed, self._last_removed = parsed, removed
        self._check_scoped_tokens(graph, scoped)
        self._fill_scoped_report(graph, reused_vertices, reused_edges, unit_reports, changed, len(parsed))
        return graph

    def _unit_has_module_expansion(self, unit: str, parsed: dict[TFDefinitionKey, Any],
                                   removed: set[TFDefinitionKey]) -> bool:
        for k, d in parsed.items():
            if unit_of_key(k) == unit and _has_module_expansion(d):
                return True
        for k, entry in self.definition_entries.items():
            if unit_of_key(k) == unit and k not in removed and k not in parsed:
                if "has_module_foreach" in entry:
                    if entry["has_module_foreach"]:
                        return True
                elif _has_module_expansion(loads(entry["definition"])):
                    return True
        return False

    def _unit_counted_statements_unchanged(self, unit: str, parsed: dict[TFDefinitionKey, Any],
                                           changed: set[TFDefinitionKey], removed: set[TFDefinitionKey],
                                           oracle: ExpansionOracle) -> bool:
        if NEGATIVE_CONTROL in ("stale_expansion", "imprecise_closure_drop_destinations", "provider_pass_aborts"):
            return False
        if unit in self._tfvar_changed_units() or unit in getattr(self, "token_units", set()):
            return False
        module_fields = loads(self.a["module"])
        changed_verts: set[int] = set()
        unit_changed_keys = {k for k in changed if unit_of_key(k) == unit}
        unit_removed_keys = {k for k in removed if unit_of_key(k) == unit}
        if unit_removed_keys:
            return False
        old_by_u = getattr(self, "_old_by_unit", None)
        unit_verts_list = old_by_u[unit] if old_by_u is not None and unit in old_by_u else [
            vi for vi, u in enumerate(self.a["unit_by_vertex"]) if u == unit
        ]
        unit_keys_list = getattr(self, "_keys_by_unit", {}).get(unit) or [self.old_keys[vi] for vi in unit_verts_list]
        unit_old_index = {k_str: vi for k_str, vi in zip(unit_keys_list, unit_verts_list)}
        old_key_of = {vi: k_str for k_str, vi in zip(unit_keys_list, unit_verts_list)}
        prev_verts = {i for k in unit_changed_keys if k in self.definition_entries
                      for i in self.definition_entries[k]["vertices"]}
        matched_verts: set[int] = set()
        changed_blocks_by_old: dict[int, Any] = {}
        for k in unit_changed_keys:
            for b in self._create_blocks(k, parsed[k], module_fields["source"],
                                         module_fields["external_modules_source_map"], module_fields["source_dir"]):
                old_i = unit_old_index.get(lookups_vertex_key(b, self.root))
                if b.block_type in FOREACH_BLOCK_TYPES and (FOREACH_STRING in b.attributes or COUNT_STRING in b.attributes):
                    from checkov.terraform.diff_scan.expansions import block_key as exp_block_key
                    if exp_block_key(b, self.root) not in oracle.records or old_i is None:
                        return False
                    probe = pickle_deepcopy(b)
                    from checkov.common.graph.graph_builder.graph_components.attribute_names import CustomAttributes
                    if isinstance(probe.config, dict):
                        probe.config.pop(CustomAttributes.VIRTUAL_RESOURCES, None)
                    probe.attributes.pop(CustomAttributes.ENCRYPTION, None)
                    probe.attributes.pop(CustomAttributes.ENCRYPTION_DETAILS, None)
                    base_b = self._reused_vertex(old_i, unit=unit)
                    ensure = getattr(base_b, "_ensure_loaded", None)
                    if ensure is not None:
                        ensure()
                    base_probe = pickle_deepcopy(base_b)
                    if isinstance(base_probe.config, dict):
                        base_probe.config.pop(CustomAttributes.VIRTUAL_RESOURCES, None)
                    base_probe.attributes.pop(CustomAttributes.ENCRYPTION, None)
                    base_probe.attributes.pop(CustomAttributes.ENCRYPTION_DETAILS, None)
                    if creation_digest(probe, self.root) != creation_digest(base_probe, self.root):
                        return False
                    prefix = b.name + "["
                    for vi in self.definition_entries.get(k, {}).get("vertices", []):
                        vname = json.loads(old_key_of[vi])[3]
                        if vname == b.name or vname.startswith(prefix):
                            matched_verts.add(vi)
                    continue
                if old_i is None:
                    return False
                matched_verts.add(old_i)
                cd_u = getattr(self, "_cd_by_unit", {}).get(unit)
                if isinstance(cd_u, dict):
                    old_cd = cd_u.get(old_i, "")
                elif cd_u is not None:
                    pos_u_map = getattr(self, "_pos_u_by_unit", None)
                    if pos_u_map is None:
                        pos_u_map = {}
                        self._pos_u_by_unit = pos_u_map
                    if unit not in pos_u_map:
                        pos_u_map[unit] = {oi: pi for pi, oi in enumerate(unit_verts_list)}
                    old_cd = cd_u[pos_u_map[unit][old_i]]
                else:
                    old_cd = self.a["creation_digests"][old_i]
                if old_cd != creation_digest(b, self.root):
                    changed_verts.add(old_i)
                    changed_blocks_by_old[old_i] = b
        if prev_verts - matched_verts:
            return False
        if changed_verts:
            unit_buckets: set[str] = set()
            fp_u = getattr(self, "_fp_by_unit", {}).get(unit)
            pos_u_map = getattr(self, "_pos_u_by_unit", None)
            if pos_u_map is None:
                pos_u_map = {}
                self._pos_u_by_unit = pos_u_map
            if unit not in pos_u_map:
                pos_u_map[unit] = {oi: pi for pi, oi in enumerate(unit_verts_list)}
            for old_i in changed_verts:
                pos_u = pos_u_map[unit][old_i]
                old_fp = fp_u[pos_u] if fp_u is not None else self.a["fingerprints"][old_i]
                if old_fp != lookups.edge_fingerprint(changed_blocks_by_old[old_i]):
                    unit_buckets.update(lookups.buckets_from_vertex_key(old_key_of[old_i]))
            if unit_buckets:
                pr_u = getattr(self, "_probes_by_unit", {}).get(unit)
                for new_vi, vi in enumerate(unit_verts_list):
                    p_list = pr_u.get(str(new_vi), []) if pr_u is not None else self.a["probes"].get(str(vi), [])
                    if unit_buckets & set(p_list):
                        return False
            from checkov.terraform.graph_builder.utils import get_referenced_vertices_in_value
            from checkov.common.graph.graph_builder import reserved_attribute_names
            types_set, pr_aliases = self._pr_global_tokens(parsed, removed)
            types_list = sorted(types_set)
            aliases_dict = {n: {"block_type_": bt} for n, bt in pr_aliases}
            for old_i, b in changed_blocks_by_old.items():
                old_b = self._reused_vertex(old_i, unit=unit)
                ensure = getattr(old_b, "_ensure_loaded", None)
                if ensure is not None:
                    ensure()
                old_refs = {
                    (attr, r.block_type, tuple(r.sub_parts), r.origin_value)
                    for attr, val in old_b.attributes.items() if attr not in reserved_attribute_names
                    for r in get_referenced_vertices_in_value(val, aliases_dict, types_list)
                }
                new_refs = {
                    (attr, r.block_type, tuple(r.sub_parts), r.origin_value)
                    for attr, val in b.attributes.items() if attr not in reserved_attribute_names
                    for r in get_referenced_vertices_in_value(val, aliases_dict, types_list)
                }
                if old_refs != new_refs:
                    return False
        referrers: dict[int, list[tuple[int, str]]] = defaultdict(list)
        edges_by_u = getattr(self, "_edges_by_unit", None)
        unit_edge_rows = edges_by_u.get(unit, []) if edges_by_u is not None else [
            r for r in self.a["edges"] if self.a["unit_by_vertex"][r[0]] == unit
        ]
        for origin, dest, label, _, _ in unit_edge_rows:
            referrers[dest].append((origin, label))
        tainted_items: list[tuple[int, Optional[str]]] = []
        for old_i, b in list(changed_blocks_by_old.items()):
            old_b = self._reused_vertex(old_i)
            ensure = getattr(old_b, "_ensure_loaded", None)
            if ensure is not None:
                ensure()
            if b.block_type == BlockType.MODULE:
                if old_b.attributes.get("source") != b.attributes.get("source") \
                        or old_b.attributes.get("version") != b.attributes.get("version") \
                        or set(old_b.attributes) != set(b.attributes):
                    return False
                diff_attrs = {a for a in b.attributes if old_b.attributes.get(a) != b.attributes.get(a)}
                for origin, _ in referrers.get(old_i, []):
                    o_ident = json.loads(old_key_of[origin])
                    if o_ident[2] == BlockType.VARIABLE and o_ident[3] in diff_attrs:
                        tainted_items.append((origin, None))
                    elif o_ident[2] != BlockType.VARIABLE:
                        tainted_items.append((origin, None))
            elif b.block_type in ("resource", "data") and os.getenv("CHECKOV_DIFF_PRECISE_CLOSURE", "false").lower() == "true":
                all_keys = set(old_b.attributes) | set(b.attributes)
                for a in all_keys:
                    if old_b.attributes.get(a) != b.attributes.get(a):
                        tainted_items.append((old_i, a))
            else:
                tainted_items.append((old_i, None))
        counted_blocks_set: set[tuple[str, str, str, str]] = set()
        for k, rec in oracle.records.items():
            if not k.startswith("module-level:") and "statement" in rec:
                ident = json.loads(k)
                call_path = ident[1][0][0] if ident[1] else ident[0]
                if os.path.dirname(call_path.replace(ROOT, self.root)) == unit:
                    if rec["statement"] == []:
                        return False
                    counted_blocks_set.add((ident[0], json.dumps(ident[1], sort_keys=True), ident[2], ident[3]))
        counted_origins: set[int] = set()
        if counted_blocks_set:
            for vi in unit_verts_list:
                vident = json.loads(old_key_of[vi])
                bkey = (vident[0], json.dumps(vident[1], sort_keys=True), vident[2], vident[3].split("[", 1)[0])
                if bkey in counted_blocks_set:
                    counted_origins.add(vi)
        stack = list(tainted_items)
        visited_full: set[int] = {v for v, a in tainted_items if a is None}
        visited_attr: set[tuple[int, str]] = {(v, a) for v, a in tainted_items if a is not None}
        from checkov.common.runners.base_runner import strtobool
        data_foreach_enabled = bool(strtobool(os.getenv("CHECKOV_ENABLE_DATAS_FOREACH_HANDLING", "False")))
        precise = os.getenv("CHECKOV_DIFF_PRECISE_CLOSURE", "false").lower() == "true"
        while stack:
            curr, tainted_attr = stack.pop()
            if curr in counted_origins and tainted_attr is None:
                return False
            if curr in counted_origins and tainted_attr in ("count", "for_each"):
                return False
            curr_ident = json.loads(old_key_of[curr])
            curr_type, curr_name = curr_ident[2], curr_ident[3].split("[", 1)[0]
            for origin, label in referrers.get(curr, []):
                if tainted_attr is not None and curr_type in ("resource", "data"):
                    orig_b = self._reused_vertex(origin, unit=unit)
                    ensure = getattr(orig_b, "_ensure_loaded", None)
                    if ensure is not None:
                        ensure()
                    val = orig_b.attributes.get(label)
                    refs = get_referenced_vertices_in_value(val, aliases_dict, types_list)
                    reads_tainted = False
                    matching_refs = [r for r in refs if r.block_type == curr_type and (
                        ".".join(r.sub_parts) == curr_name or ".".join(r.sub_parts).startswith(curr_name + ".")
                    )]
                    if not matching_refs:
                        reads_tainted = True
                    else:
                        for r in matching_refs:
                            j = ".".join(r.sub_parts)
                            if j == curr_name:
                                reads_tainted = True
                            else:
                                suffix = j[len(curr_name) + 1:].split(".")[0]
                                if suffix == tainted_attr.split(".")[0] or curr_type == BlockType.DATA and suffix in ("binding", "policy_data"):
                                    reads_tainted = True
                    if not reads_tainted:
                        continue
                if label in ("count", "for_each") or label.startswith(("count.", "for_each.")):
                    o_type = json.loads(old_key_of[origin])[2]
                    if o_type != BlockType.DATA or data_foreach_enabled:
                        return False
                o_type = json.loads(old_key_of[origin])[2]
                if precise and o_type in ("resource", "data"):
                    if (origin, label) not in visited_attr and origin not in visited_full:
                        visited_attr.add((origin, label))
                        stack.append((origin, label))
                    if origin in counted_origins:
                        vident = json.loads(old_key_of[origin])
                        bkey = (vident[0], json.dumps(vident[1], sort_keys=True), vident[2], vident[3].split("[", 1)[0])
                        for sib in counted_origins:
                            if (sib, label) not in visited_attr and sib not in visited_full:
                                sident = json.loads(old_key_of[sib])
                                if (sident[0], json.dumps(sident[1], sort_keys=True), sident[2], sident[3].split("[", 1)[0]) == bkey:
                                    visited_attr.add((sib, label))
                                    stack.append((sib, label))
                else:
                    if origin in counted_origins:
                        return False
                    if origin not in visited_full:
                        visited_full.add(origin)
                        stack.append((origin, None))
        for k, rec in oracle.records.items():
            if not k.startswith("module-level:") and "statement" in rec:
                ident = json.loads(k)
                call_path = ident[1][0][0] if ident[1] else ident[0]
                if os.path.dirname(call_path.replace(ROOT, self.root)) == unit:
                    oracle.decided[k] = rec["statement"]
                    oracle.reused.append(k)
        return True

    def _instance_level_unit(self, unit: str, parsed: dict[TFDefinitionKey, Any], changed: set[TFDefinitionKey],
                             removed: set[TFDefinitionKey], module_fields: dict[str, Any],
                             global_types: set[str],
                             global_aliases: set[tuple[str, str]]) -> Optional[tuple["_UnitResult", dict[str, Any]]]:
        """Round 8: a unit with count / for_each updated per block instead of rebuilt. Statements are decided on the
        unit's PRE-EXPANSION graph (vertices + edges as Checkov's first _build_edges pass leaves them): unchanged read
        closure -> baseline statement, else Checkov's own static / dynamic evaluation for those blocks only. Blocks
        whose creation state and statement are unchanged keep their baseline instances; the others are re-expanded
        with Checkov's instance code; the unit then goes through the per-owner edge engine. None -> the caller falls
        back to the whole-unit rebuild (module count / for_each, enabled data expansion, anything not reproducible)."""
        if self._unit_has_module_expansion(unit, parsed, removed):
            return None
        oracle = self._expansion_oracle()
        assert oracle is not None
        try:
            if not self._unit_counted_statements_unchanged(unit, parsed, changed, removed, oracle):
                definitions = self._unit_definitions(unit, parsed, removed)
                tfvars = self._unit_tfvar_blocks(unit)
                if not definitions and not tfvars:
                    return None
                self._decide_unit_statements(definitions, tfvars, module_fields, global_types, global_aliases, oracle)
            sub = DiffEngine.__new__(DiffEngine)
            sub.__init__(self._unit_artifact(unit), self.root, self.changes)
            if getattr(self, "_cached_old_types", None) is None:
                self._cached_old_types = {t for d in self.definition_entries.values() for t in d["resource_types"]}
            sub._cached_old_types = self._cached_old_types
            sub._global_parsed_and_removed = (parsed, removed, self.definition_entries, self.a["aliases"],
                                              self.a["alias_keys"], global_types, global_aliases)
            if getattr(self, "new_tfvar_blocks", None) is not None:
                sub.unit_tfvar_blocks = self._unit_tfvar_blocks(unit)
            unit_parsed = {k: v for k, v in parsed.items() if unit_of_key(k) == unit}
            unit_changed = {k for k in changed if unit_of_key(k) == unit}
            unit_removed = {k for k in removed if unit_of_key(k) == unit}
            splicer = InstanceSplicer(sub, oracle)
            vertices, fresh = splicer.vertices(unit_parsed, unit_changed, unit_removed, module_fields)
            graph = sub._per_owner_graph(vertices, fresh, unit_parsed, unit_changed, unit_removed, module_fields)
        except IncrementalGraphUnsupported as error:
            self.instance_level_fallbacks[unit] = str(error)
            return None
        stats = dict(splicer.stats)
        exp_rep = self._expansion_report(oracle)
        sub.release_pre_render_state()
        report = {"mode": "instance-level", "vertices": sub.report.vertices,
                  "vertices_rebuilt": sub.report.vertices_rebuilt, "edges": sub.report.edges,
                  "edges_rebuilt": sub.report.edges_rebuilt, "edge_owners_rebuilt": sub.report.edge_owners_rebuilt,
                  **stats, **exp_rep}
        return _UnitResult(graph, sub.report, sub), report

    def _decide_unit_statements(self, definitions: dict[TFDefinitionKey, Any], tfvars: list[Any],
                                module_fields: dict[str, Any], global_types: set[str],
                                global_aliases: set[tuple[str, str]], oracle: ExpansionOracle) -> None:
        """Checkov's pre-expansion graph of the unit (vertex creation + one edge pass, no expansion), then the oracle
        decides every counted block's statement on it (reuse / recompute). Cheap: no expansion, no post-expansion
        edge passes; the sub-graph render, when needed, covers only the read closures of recomputed blocks."""
        graph = pre_expansion_unit_graph(definitions, tfvars, module_fields, global_types,
                                         {n: {"block_type_": b} for n, b in global_aliases})
        from checkov.terraform.graph_builder.foreach.foreach_entity_handler import ForeachEntityHandler

        for block_type in (BlockType.RESOURCE, BlockType.DATA):
            handler = ForeachEntityHandler(graph, block_type)
            blocks = [i for i, v in enumerate(graph.vertices) if v.block_type == block_type and is_expanded(v)]
            if blocks:
                oracle.statements(handler, blocks)

    def _expansion_oracle(self) -> Optional[ExpansionOracle]:
        """One oracle per unit build: count / for_each statements whose read closure is unchanged are reused from the
        baseline (CHECKOV_DIFF_REUSE_EXPANSIONS, default on in the diff scan; off = Round 6 behaviour)."""
        if os.getenv(REUSE_EXPANSIONS_ENV, "false").lower() != "true" or "expansions" not in self.a:
            return None
        return ExpansionOracle(self.root, self.a["expansions"])

    @staticmethod
    def _expansion_report(oracle: Optional[ExpansionOracle]) -> dict[str, Any]:
        if oracle is None:
            return {}
        return {"expansions_reused": len(oracle.reused), "expansions_recomputed": len(oracle.recomputed),
                "expansions_changed": sorted(_short_block(k) for k in oracle.changed),
                "module_levels_reused": oracle.module_levels_reused,
                "module_levels_recomputed": oracle.module_levels_recomputed}

    def _assemble(self, vertices: list[Any], edges: list[tuple[int, int, str]], parsed: dict[TFDefinitionKey, Any],
                  removed: set[TFDefinitionKey], changed: set[TFDefinitionKey],
                  module_fields: dict[str, Any]) -> TerraformLocalGraph:
        module = Module(source_dir=module_fields["source_dir"],
                        external_modules_source_map=module_fields["external_modules_source_map"])
        module.source = module_fields["source"]
        module.blocks = vertices
        lazy_filter = os.getenv("CHECKOV_INCREMENTAL_LAZY_FINAL_STATE", "false").lower() == "true"
        kept = {
            k: d for k, d in self.definition_entries.items()
            if k not in removed and k not in changed
            and (not lazy_filter or not isinstance(d, dict) or d.get("has_provider_or_module", True))
        }
        module.temp_tf_definition = LazyDefinitions(kept, dict(parsed))
        module.temp_tf_definition._total_len = len(
            (set(self.definition_entries) - set(removed)) | set(parsed)
        )
        pr_types, _ = self._pr_global_tokens(parsed, removed)
        module.resources_types = set(pr_types)
        graph = TerraformLocalGraph(module)
        graph.vertices = vertices
        if os.getenv("CHECKOV_INCREMENTAL_LAZY_FINAL_STATE", "false").lower() == "true":
            for i in range(len(vertices)):
                b = vertices[i]
                if b.block_type in (BlockType.RESOURCE, BlockType.PROVIDER):
                    graph.vertices_by_block_type[b.block_type].append(i)
                    if b.block_type == BlockType.PROVIDER:
                        graph.vertices_by_module_dependency[b.source_module_object][b.block_type].append(i)
            graph.edges = [None] * len(edges)  # type: ignore[list-item]
            out_e = defaultdict(list)
            in_e = defaultdict(list)
            for idx_e, (o, d, lbl) in enumerate(edges):
                e_obj = Edge(o, d, lbl)
                graph.edges[idx_e] = e_obj
                out_e[o].append(e_obj)
                in_e[d].append(e_obj)
            graph.out_edges = out_e
            graph.in_edges = in_e
            graph.dfo_set_edges_consistent = True  # type: ignore[attr-defined]
            edges.clear()
        else:
            graph._arrange_graph_data()
            set_edges(graph, edges)
        self._definitions = module.temp_tf_definition
        return graph

    def _check_scoped_tokens(self, graph: TerraformLocalGraph, scoped: set[str]) -> None:
        """A unit built alone sees only its own resource types / aliases; Checkov's full build sees every unit's.
        Reused units: a token that appeared/disappeared must not be mentioned by them (else their edges may change).
        Scoped units: they must not mention a token that exists only in OTHER units (else the full build would
        resolve a reference the unit build could not)."""
        tokens = self._global_tokens_changed(graph)
        if tokens and (getattr(self, "_cached_token_units", None) is None or NEGATIVE_CONTROL == "no_global_token_units"):
            touched = set(scoped) | set(getattr(self, "touched_units", set()))
            for index, vertex in enumerate(graph.vertices):
                if unit_of_vertex(vertex) not in touched:
                    if isinstance(vertex, LazyTerraformBlock) and not vertex._loaded and isinstance(vertex._loader, tuple):
                        raw_b = vertex._loader[0]["vertices"][vertex._loader[1]]
                        if not any(t.encode() in raw_b for t in tokens):
                            continue
                    if _mentions(vertex, tokens):
                        raise IncrementalGraphUnsupported(
                            f"unchanged unit vertex {vertex.name} mentions an added/removed resource type or alias")
        # Scoped units are built with the PR-wide lookup lists (build_unit global_*): verify the assembled graph's own
        # lists equal the ones the units were built with, i.e. the precomputation from definitions was exact.
        types, aliases = self._pr_global_tokens(self._last_parsed, self._last_removed)
        if set(graph.get_resources_types_in_graph()) != types:
            raise IncrementalGraphUnsupported("global resource-type list of the assembled graph differs from the one "
                                              "scoped units were built with")
        if scoped:
            kept_defs = {k for k in self.definition_entries if k not in self._last_removed and k not in self._last_parsed}
            scoped_aliases = {(v.name, str(v.block_type)) for v in graph.vertices
                              if unit_of_vertex(v) in scoped and "alias" in v.attributes and v.block_type != BlockType.TF_VARIABLE}
            expected_scoped_aliases = {a for a in aliases if any(unit_of_key(k) in scoped and k in kept_defs
                                                                 for k in (loads(pk) for pk in self.a["alias_keys"].get(a[0], [])))}
            for k, d in self._last_parsed.items():
                if unit_of_key(k) in scoped:
                    for provider in d.get(BlockType.PROVIDER, []):
                        for name, attrs in provider.items():
                            if isinstance(attrs, dict) and attrs.get("alias"):
                                expected_scoped_aliases.add((f"{name}.{attrs['alias'][0]}", str(BlockType.PROVIDER)))
            if scoped_aliases != expected_scoped_aliases:
                raise IncrementalGraphUnsupported("global provider-alias list of the assembled graph differs from the one "
                                                  "scoped units were built with")

    def _fill_scoped_report(self, graph: TerraformLocalGraph, reused_vertices: int, reused_edges: int,
                            unit_reports: dict[str, Any], changed: set[TFDefinitionKey], reparsed: int) -> None:
        r = self.report
        r.definition_keys = len(graph.module.temp_tf_definition)
        r.definition_keys_reparsed = reparsed
        r.vertices = len(graph.vertices)
        r.vertices_reused = reused_vertices
        r.vertices_rebuilt = r.vertices - reused_vertices
        old_cnt = getattr(self, "_old_keys_count", None)
        if old_cnt is None:
            old_cnt = len(self.old_keys)
        if r.vertices_rebuilt == 0 and r.vertices == old_cnt:
            r.vertices_added = []
            r.vertices_removed = []
        elif getattr(self, "_keys_by_unit", None) and getattr(self, "touched_units", None):
            touched_u = self.touched_units
            old_t_set = {k for u in touched_u for k in self._keys_by_unit.get(u, ())}
            new_t_set = {
                lookups_vertex_key(v, self.root) for v in graph.vertices
                if unit_of_vertex(v) in touched_u
            }
            r.vertices_added = sorted(_short(k) for k in new_t_set - old_t_set)
            r.vertices_removed = sorted(_short(k) for k in old_t_set - new_t_set)
        else:
            new_keys = vertex_keys(graph, self.root)
            old_keys_list = self.old_keys or self.a["keys"]
            old_set, new_set = set(old_keys_list), set(new_keys)
            r.vertices_added = sorted(_short(k) for k in new_set - old_set)
            r.vertices_removed = sorted(_short(k) for k in old_set - new_set)
        r.edges = len(graph.edges)
        r.edges_reused = reused_edges
        r.edges_rebuilt = r.edges - reused_edges
        r.scoped_units = {os.path.relpath(u, self.root): v for u, v in unit_reports.items()}
        r.units_total = self._total_units_count if getattr(self, "_total_units_count", None) is not None else len(self.a["units"])
        unit_set = self._unit_names_set if getattr(self, "_unit_names_set", None) is not None else set(self.a["units"])
        r.units_reused = r.units_total - len([u for u in unit_reports if u in unit_set])
        instances = {k.tf_source_modules for k in self.definition_entries if k not in self._last_removed
                     and k.tf_source_modules} | {k.tf_source_modules for k in self._last_parsed if k.tf_source_modules}
        scoped_units = {u for u, v in unit_reports.items() if v.get("mode") == "scoped-rebuild"}
        updated = {k.tf_source_modules for k in self.definition_entries
                   if k not in self._last_removed and k.tf_source_modules and unit_of_key(k) in scoped_units}
        updated |= {k.tf_source_modules for k in self._last_parsed
                    if k.tf_source_modules and unit_of_key(k) in scoped_units}
        updated |= {k.tf_source_modules for k in changed if k.tf_source_modules}
        r.module_instances = len(instances)
        r.module_instances_updated = sorted(f"{m.name}@{os.path.relpath(m.path, self.root)}" for m in updated)
        r.module_instances_reused = len(instances - updated)
        r.edge_owners_rebuilt = sorted(o for v in unit_reports.values() for o in v.get("edge_owners_rebuilt", []))
        r.mode = "units"

    def release_pre_render_state(self) -> None:
        """Drop what only the pre-render build reads: the unpickled baseline vertices that were not reused (reused ones
        live on in the PR graph), and the old-key index. The baseline definitions stay: module.temp_tf_definition
        (LazyDefinitions) unpickles them on demand during the post-render passes."""
        self._reused_vertex_cache = {}
        self.old_index = {}
        self.old_keys = []
        self.definition_entries = {}
        self.pickled_definitions = {}
        self._chain_cache = {}
        self._global_parsed_and_removed = None
        self._cached_pr_global_tokens = None
        self._cached_old_types = None
        self._cached_token_units = None
        self._defs_by_unit = None
        self._old_by_unit = None
        self._edges_by_unit = None
        self._sm_by_unit = {}
        self._mc_by_unit = {}
        self._cd_by_unit = {}
        self._scoped_cd_cache = {}
        self._total_units_count = None
        self._unit_names_set = None
        self._fp_by_unit = {}
        self._probes_by_unit = {}
        self._keys_by_unit = {}
        self._old_keys_count = None
        if getattr(self, "_definitions", None) is not None \
                and os.getenv("CHECKOV_INCREMENTAL_LAZY_FINAL_STATE", "false").lower() == "true":
            self._definitions._total_len = len(self._definitions)
            self._definitions._pickled = {
                k: v for k, v in self._definitions._pickled.items()
                if not isinstance(v, dict) or v.get("has_provider_or_module", True)
            }
        self.a = {}

    def install_resolved_swaps(self, graph: TerraformLocalGraph) -> int:
        """Callers whose `__resolved__` was patched (module_files.py): register (baseline, PR) values so rendering
        treats a caller with no other change as unchanged (incremental_graph.RESOLVED_SWAPS)."""
        from checkov.terraform.graph_builder import incremental_graph

        incremental_graph.RESOLVED_SWAPS.clear()
        patches = getattr(self, "resolved_patches", {})
        if not patches:
            return 0
        for vertex in graph.vertices:
            if vertex.block_type != BlockType.MODULE:
                continue
            old = patches.get((vertex.path, vertex.source_module_object, vertex.name))
            call = vertex.config.get(vertex.name) if isinstance(vertex.config, dict) else None
            if old is None or not isinstance(call, dict):
                continue
            current = call.get(RESOLVED_MODULE_ENTRY_NAME)
            restored = incremental_graph._restore(incremental_graph._anonymise(current, self.root), self.root)
            incremental_graph.RESOLVED_SWAPS[incremental_graph.vertex_key(vertex, self.root)] = (old, restored)
        return len(incremental_graph.RESOLVED_SWAPS)

    def finish(self) -> PreRenderReport:
        self.report.definitions_unpickled_for_post_render = self._definitions.unpickled
        return self.report

    def _fill_report(self, graph: TerraformLocalGraph, new_keys: list[str], fresh: set[int],
                     rebuild: dict[int, str], changed: set[TFDefinitionKey], reparsed: int) -> None:
        r = self.report
        old_set, new_set = set(self.old_keys), set(new_keys)
        r.definition_keys = len(graph.module.temp_tf_definition)
        r.definition_keys_reparsed = reparsed
        r.vertices = len(new_keys)
        r.vertices_rebuilt = len(fresh)
        r.vertices_reused = r.vertices - r.vertices_rebuilt
        r.vertices_added = sorted(_short(k) for k in new_set - old_set)
        r.vertices_removed = sorted(_short(k) for k in old_set - new_set)
        r.vertices_changed = sorted(_short(new_keys[i]) for i in fresh if new_keys[i] in old_set)
        r.edges = len(graph.edges)
        r.edge_owners_rebuilt = sorted(_short(new_keys[i]) for i in rebuild)
        for reason in rebuild.values():
            r.edge_owner_reasons[reason] = r.edge_owner_reasons.get(reason, 0) + 1
        instances = {k.tf_source_modules for k in self.definition_entries if k not in self._last_removed
                     and k.tf_source_modules} | {k.tf_source_modules for k in self._last_parsed if k.tf_source_modules}
        updated = {k.tf_source_modules for k in changed if k.tf_source_modules}
        r.module_instances = len(instances)
        r.module_instances_updated = sorted(f"{m.name}@{os.path.relpath(m.path, self.root)}" for m in updated)
        r.module_instances_reused = len(instances - updated)


class _ArtifactOverlay:
    """A unit's view of the artifact: re-indexed sections from `overrides`, every other section read from `base` on
    access (a section store decodes only what the unit engine actually reads)."""

    def __init__(self, base: Any, overrides: dict[str, Any]) -> None:
        self._base = base
        self._overrides = overrides

    def __getitem__(self, name: str) -> Any:
        return self._overrides[name] if name in self._overrides else self._base[name]

    def get(self, name: str, default: Any = None) -> Any:
        return self[name] if name in self else default

    def __contains__(self, name: object) -> bool:
        return name in self._overrides or name in self._base


@dataclass
class _UnitResult:
    graph: TerraformLocalGraph
    report: PreRenderReport
    engine: Optional[Any] = None


def _mentions(vertex: Any, tokens: set[str]) -> bool:
    text = json.dumps(vertex.attributes, default=str)
    return any(token in text for token in tokens)


def _mentions_reference(vertex: Any, tokens: set[str]) -> bool:
    """`token.` appears in an attribute value, i.e. a possible reference `aws_x.name` / `alias.attr`."""
    text = json.dumps(vertex.attributes, default=str)
    return any(f"{token}." in text for token in tokens)


def lookups_vertex_key(block: Any, root: str) -> str:
    from checkov.terraform.graph_builder.incremental_graph import vertex_key

    return vertex_key(block, root)


def build_pr_pre_render_graph(artifact: dict[str, Any], root: str, changes: ChangeSet) -> tuple[TerraformLocalGraph,
                                                                                                 DiffEngine]:
    engine = DiffEngine(artifact, root, changes)
    return engine.build(), engine


