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
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Iterable, Optional

from checkov.common.graph.graph_builder import Edge
from checkov.common.util.consts import RESOLVED_MODULE_ENTRY_NAME
from checkov.common.util.data_structures_utils import pickle_deepcopy
from checkov.terraform.graph_builder.foreach.consts import COUNT_STRING, FOREACH_STRING
from checkov.terraform.graph_builder.graph_components.block_types import BlockType
from checkov.terraform.graph_builder.graph_components.generic_resource_encryption import ENCRYPTION_BY_RESOURCE_TYPE
from checkov.terraform.graph_builder.graph_components.module import Module
from checkov.terraform.graph_builder.incremental_graph import IncrementalGraphUnsupported, vertex_keys
from checkov.terraform.graph_builder.local_graph import TerraformLocalGraph
from checkov.terraform.modules.module_objects import TFDefinitionKey
from checkov.terraform.modules.module_utils import clean_parser_types, serialize_definitions
from checkov.terraform.parser_utils import load_or_die_quietly

from checkov.terraform.diff_scan import lookups
from checkov.terraform.diff_scan.artifact import ARTIFACT_VERSION, loads
from checkov.terraform.diff_scan.baseline import aliases_signature, creation_digest, resource_types_of, tf_var_environment
from checkov.terraform.diff_scan.expansions import ExpansionOracle
from checkov.terraform.diff_scan.instance_update import InstanceSplicer, instance_update_enabled, is_expanded
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
    mode: str = "per-owner"
    """per-owner: every unit spliced, edges rebuilt per owner | scoped-units: changed units rebuilt by Checkov"""
    units_total: int = 0
    units_reused: int = 0
    scoped_units: dict[str, Any] = field(default_factory=dict)
    renamed_files: list[dict[str, str]] = field(default_factory=list)
    """pure order-preserving renames applied to the artifact instead of re-parsing (rename.py)"""


@dataclass
class ChangeSet:
    changed: list[str]
    """absolute paths of added / modified files; their content is on disk"""
    deleted: list[str]
    """absolute paths of deleted files (renames / moves are a delete plus an add)"""


class LazyDefinitions(dict):  # type: ignore[type-arg]
    """module.temp_tf_definition for the post-render provider pass: baseline definitions are unpickled on first access."""

    def __init__(self, pickled: dict[TFDefinitionKey, str], parsed: dict[TFDefinitionKey, Any]) -> None:
        super().__init__()
        self._pickled = pickled
        self._parsed = parsed
        self.unpickled = 0

    def _load(self, key: Any) -> Any:
        if key in self._parsed:
            return self._parsed[key]
        if key not in self._pickled:
            raise KeyError(key)
        self._parsed[key] = loads(self._pickled[key])
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
        self.old_keys: list[str] = artifact["keys"]
        self.old_index = {k: i for i, k in enumerate(self.old_keys)}
        self.pickled_definitions = {loads(d["key"]): d["definition"] for d in artifact["definitions"]}
        self.definition_entries = {loads(d["key"]): d for d in artifact["definitions"]}
        self._reused_vertex_cache: dict[int, Any] = {}
        self.instance_level_fallbacks: dict[str, str] = {}
        if "creation_digests" not in artifact or len(artifact["creation_digests"]) < len(artifact["vertices"]):
            for i in range(len(artifact["creation_digests"]), len(artifact["vertices"])):
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
                else:
                    removed.add(key)
        return parsed, set(parsed), removed - set(parsed)

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

    def _reused_vertex(self, old_index: int) -> Any:
        if old_index not in self._reused_vertex_cache:
            self._reused_vertex_cache[old_index] = loads(self.a["vertices"][old_index])
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

    def _reuse_if_unchanged(self, block: Any, fresh: set[int], position: int) -> Any:
        key = lookups_vertex_key(block, self.root)
        old = self.old_index.get(key)
        if old is not None and self.a["creation_digests"][old] == creation_digest(block, self.root):
            return self._reused_vertex(old)
        fresh.add(position)
        return block

    # ------------------------------------------------------------------------------------------- 3 + 4. edges

    def _changed_buckets(self, new_keys: list[str], vertices: list[Any], fresh: set[int]) -> set[str]:
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
        old_types = {t for d in self.a["definitions"] for t in d["resource_types"]}
        new_types = set(graph.get_resources_types_in_graph())
        old_aliases = {name for name, _ in self.a["aliases"]}
        new_aliases = {name for name, _ in aliases_signature(graph)}
        tokens = (old_types ^ new_types) | (old_aliases ^ new_aliases)
        if {tuple(a) for a in self.a["aliases"]} != {tuple(a) for a in aliases_signature(graph)}:
            tokens |= {name for name, _ in self.a["aliases"]} | {name for name, _ in aliases_signature(graph)}
        return tokens

    def _pr_global_tokens(self, parsed: dict[TFDefinitionKey, Any], removed: set[TFDefinitionKey]) \
            -> tuple[set[str], set[tuple[str, str]]]:
        """Checkov's GLOBAL lookup lists as of the PR: resource types (Module.resources_types) and provider aliases
        (_get_aliases). Computed from definitions only (stored for unchanged keys, parsed for changed ones)."""
        kept = {k for k in self.pickled_definitions if k not in removed and k not in parsed}
        types = {t for k in kept for t in self.definition_entries[k]["resource_types"]}
        types |= {t for d in parsed.values() for t in resource_types_of(d)}
        aliases = {tuple(a) for a in self.a["aliases"]
                   if any(key in kept for key in (loads(k) for k in self.a["alias_keys"].get(a[0], [])))}
        for definition in parsed.values():
            for provider in definition.get(BlockType.PROVIDER, []):
                for name, attrs in provider.items():
                    if isinstance(attrs, dict) and attrs.get("alias"):
                        aliases.add((f"{name}.{attrs['alias'][0]}", BlockType.PROVIDER))
        return types, aliases

    def _units_reading_changed_tokens(self, parsed: dict[TFDefinitionKey, Any],
                                      removed: set[TFDefinitionKey]) -> set[str]:
        """UNIT ISOLATION: the resource-type and provider-alias lists are global, so a type/alias that appears or
        disappears ANYWHERE can change the edges (and rendering) of a vertex in an unchanged unit that mentions it.
        Such units are touched (per-owner, or scoped if they contain count/for_each) instead of spliced."""
        types, aliases = self._pr_global_tokens(parsed, removed)
        old_types = {t for d in self.a["definitions"] for t in d["resource_types"]}
        old_aliases = {tuple(a) for a in self.a["aliases"]}
        tokens = (types ^ old_types) | {n for n, _ in aliases ^ old_aliases}
        if not tokens or NEGATIVE_CONTROL == "no_global_token_units":
            return set()
        units: set[str] = set()
        for index, unit in enumerate(self.a["unit_by_vertex"]):
            if unit in units:
                continue
            if _mentions(self._reused_vertex(index), tokens):
                units.add(unit)
        self.report.global_tokens_changed = sorted(tokens)
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
            elif tokens and _mentions(graph.vertices[position], tokens):
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
        aliases = graph._get_aliases()
        resources_types = graph.get_resources_types_in_graph()
        for position, vertex in enumerate(graph.vertices):
            if position in rebuild:
                before = len(graph.edges)
                graph._build_edges_for_vertex(position, vertex, aliases, resources_types)
                graph._build_virtual_resources_edges(position, vertex)
                self.report.edges_rebuilt += len(graph.edges) - before
            else:
                self._append(graph, replay.get((position, BUILD_PHASE), []), new_keys[position])
        for position in list(graph.out_edges):
            if position in rebuild:
                before = len(graph.edges)
                graph._connect_module_provider_for_vertex(position, graph.out_edges[position])
                self.report.edges_rebuilt += len(graph.edges) - before
            else:
                self._append(graph, replay.get((position, PROVIDER_PHASE), []), new_keys[position])

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
        if reparse:
            self.extra_source_map: dict[Any, str] = {}
            graph = self._build_with_reparsed_units(parsed, changed, removed, module_fields, reparse)
            graph.module.external_modules_source_map = {**module_fields["external_modules_source_map"],
                                                        **self.extra_source_map}
            return graph
        scoped = self._scoped_units(parsed, changed, removed)
        if scoped or self.a["foreach_ran"] or self._tfvar_changed_units() \
                or self._units_reading_changed_tokens(parsed, removed):
            return self._build_with_scoped_units(parsed, changed, removed, module_fields, scoped)
        vertices, fresh = self._splice_vertices(parsed, changed, removed, module_fields)
        return self._per_owner_graph(vertices, fresh, parsed, changed, removed, module_fields)

    def _per_owner_graph(self, vertices: list[Any], fresh: set[int], parsed: dict[TFDefinitionKey, Any],
                         changed: set[TFDefinitionKey], removed: set[TFDefinitionKey],
                         module_fields: dict[str, Any]) -> TerraformLocalGraph:
        module = Module(source_dir=module_fields["source_dir"],
                        external_modules_source_map=module_fields["external_modules_source_map"])
        module.source = module_fields["source"]
        module.blocks = vertices
        kept = {k: v for k, v in self.pickled_definitions.items() if k not in removed and k not in changed}
        module.temp_tf_definition = LazyDefinitions(kept, dict(parsed))
        module.resources_types = {t for k, d in self.definition_entries.items() if k in kept
                                  for t in d["resource_types"]} | {t for d in parsed.values()
                                                                   for t in resource_types_of(d)}
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
        return {path: (loads(v) if isinstance(v, str) else v) for path, v in by_file.items()}

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
        return {unit_of_key(k) for k in self.pickled_definitions
                if k.tf_source_modules and os.path.dirname(k.file_path) in directories}

    def _reparse_reasons(self, parsed: dict[TFDefinitionKey, Any], removed: set[TFDefinitionKey],
                         module_fields: dict[str, Any]) -> dict[str, str]:
        """unit directory -> why its definition keys must be re-derived by a unit re-parse."""
        reasons: dict[str, str] = {}
        for unit in self._topology_changed_units(parsed, removed):
            reasons[unit] = "module call added/removed/re-sourced"
        if NEGATIVE_CONTROL != "no_module_fileset_rule":
            for unit in self._module_file_set_changed_units(parsed, removed):
                reasons.setdefault(unit, "file set of a loaded module directory changed (__resolved__ lists files)")
        kinds = self._baseline_directories()
        by_file = self._pr_definitions_by_file(parsed, removed)
        pr_called = {t for targets in self._local_call_targets(
            {TFDefinitionKey(p): d for p, d in by_file.items()}).values() for t in targets}
        for path in self.new_directory_files:
            directory = os.path.dirname(path)
            if directory in pr_called:
                callers = [k for k in self.pickled_definitions if os.path.dirname(k.file_path) == directory]
                if not callers:
                    reasons.update({unit_of_key(TFDefinitionKey(p)): "new local module directory called"
                                    for p, d in by_file.items()
                                    if directory in self._local_call_targets({TFDefinitionKey(p): d}).get(
                                        os.path.dirname(p), set())})
            else:
                reasons[directory] = "new root directory"
        for directory, kind in kinds.items():
            if is_external_module_path(directory, self.root):
                continue
            now_called = directory in pr_called
            if kind == "unit" and now_called:
                reasons[directory] = "root directory became a called module"
            if kind == "module" and not now_called and any(os.path.dirname(p) == directory for p in by_file):
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
        stored = {p: lines for p, lines in self.a["files"].items() if is_external_module_path(p, self.root)}
        current: dict[str, list[str]] = {}
        materialized = os.path.join(self.root, ".external_modules")
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

    def _unit_module_dirs(self, unit: str, by_file: dict[str, Any]) -> tuple[set[str], set[str]]:
        """(local module directories reachable from the unit, external module directories it uses)."""
        definitions = {TFDefinitionKey(p): d for p, d in by_file.items() if not is_external_module_path(p, self.root)}
        targets = self._local_call_targets(definitions)
        reachable: set[str] = set()
        pending = [unit]
        while pending:
            directory = pending.pop()
            for target in targets.get(directory, set()):
                if target not in reachable and target != unit:
                    reachable.add(target)
                    pending.append(target)
        return reachable, set()

    def _reparsed_unit_definitions(self, unit: str, by_file: dict[str, Any], files: dict[str, list[str]],
                                   pr_units: set[str]) -> tuple[dict[TFDefinitionKey, Any], dict[str, Any]]:
        module_dirs, _ = self._unit_module_dirs(unit, by_file)
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
        by_file = self._pr_definitions_by_file(parsed, removed)
        files = dict(self.a["files"])
        for path in self.changes.deleted:
            files.pop(path, None)
        for path in self.changes.changed:
            if not is_variable_file(path):
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
        kinds = self._baseline_directories()
        pr_called = {t for ts in self._local_call_targets({TFDefinitionKey(p): d for p, d in by_file.items()}).values()
                     for t in ts}
        pr_units = {u for u, k in kinds.items() if k == "unit"} | {os.path.dirname(p) for p in self.new_directory_files}
        pr_units = {u for u in pr_units if u not in pr_called} | {u for u in reasons}
        reparsed: dict[str, dict[TFDefinitionKey, Any]] = {}
        tfvars_by_unit: dict[str, list[Any]] = {}
        new_tfvars = getattr(self, "new_tfvar_blocks", None)
        for unit in sorted(reasons):
            definitions, external_vars = self._reparsed_unit_definitions(unit, by_file, files, pr_units)
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
            before = key in self.pickled_definitions and has_count_or_foreach(loads(self.pickled_definitions[key]))
            after = key in parsed and has_count_or_foreach(parsed[key])
            if before or after:
                scoped.add(unit)

        module_fields = loads(self.a["module"])
        truly_changed_vertices: set[int] = set()
        for key in changed:
            blocks = self._create_blocks(key, parsed[key], module_fields["source"],
                                         module_fields["external_modules_source_map"], module_fields["source_dir"])
            for block in blocks:
                vk = lookups_vertex_key(block, self.root)
                old_idx = self.old_index.get(vk)
                if old_idx is None or self.a["creation_digests"][old_idx] != creation_digest(block, self.root):
                    if old_idx is not None:
                        truly_changed_vertices.add(old_idx)
                    if block.block_type in FOREACH_BLOCK_TYPES and (
                            FOREACH_STRING in block.attributes or COUNT_STRING in block.attributes):
                        scoped.add(unit_of_key(key))
        for key in removed:
            entry = self.definition_entries.get(key)
            if entry:
                truly_changed_vertices.update(entry["vertices"])

        if getattr(self, "new_tfvar_blocks", None) is not None:
            truly_changed_vertices.update(self.a.get("tfvar_vertices", []))

        referrers: dict[int, list[tuple[int, str]]] = defaultdict(list)
        if NEGATIVE_CONTROL != "ignore_count_dependencies":
            for origin, dest, label, _, _ in self.a["edges"]:
                referrers[dest].append((origin, label))

        stack = list(truly_changed_vertices)
        visited = set(truly_changed_vertices)
        while stack:
            curr = stack.pop()
            for origin, label in referrers.get(curr, []):
                if label in ("count", "for_each"):
                    scoped.add(self.a["unit_by_vertex"][origin])
                if origin not in visited:
                    visited.add(origin)
                    stack.append(origin)

        return scoped

    def _unit_artifact(self, unit: str) -> dict[str, Any]:
        """The artifact restricted to one unit (no count/for_each in it): vertex lists, edges, probes re-indexed."""
        members = [i for i, u in enumerate(self.a["unit_by_vertex"]) if u == unit]
        position = {old: new for new, old in enumerate(members)}
        definitions = []
        for entry in self.a["definitions"]:
            if unit_of_key(loads(entry["key"])) == unit:
                definitions.append({**entry, "vertices": [position[i] for i in entry["vertices"]]})
        return _ArtifactOverlay(self.a, {
            "keys": [self.a["keys"][i] for i in members],
            "vertices": [self.a["vertices"][i] for i in members],
            "creation_digests": [self.a["creation_digests"][i] for i in members],
            "fingerprints": [self.a["fingerprints"][i] for i in members],
            "tfvar_vertices": [position[i] for i in self.a["tfvar_vertices"] if i in position],
            "edges": [[position[o], position[d], label, position[w], phase]
                      for o, d, label, w, phase in self.a["edges"] if o in position],
            "probes": {str(position[int(i)]): p for i, p in self.a["probes"].items() if int(i) in position},
            "definitions": definitions,
            "foreach_ran": False,
            "global_positions": members,
        })

    def _per_owner_unit(self, unit: str, parsed: dict[TFDefinitionKey, Any], changed: set[TFDefinitionKey],
                        removed: set[TFDefinitionKey], module_fields: dict[str, Any]) -> "_UnitResult":
        sub = DiffEngine.__new__(DiffEngine)
        sub.__init__(self._unit_artifact(unit), self.root, self.changes)
        if getattr(self, "new_tfvar_blocks", None) is not None:
            sub.unit_tfvar_blocks = self._unit_tfvar_blocks(unit)
        unit_parsed = {k: v for k, v in parsed.items() if unit_of_key(k) == unit}
        unit_changed = {k for k in changed if unit_of_key(k) == unit}
        unit_removed = {k for k in removed if unit_of_key(k) == unit}
        vertices, fresh = sub._splice_vertices(unit_parsed, unit_changed, unit_removed, module_fields)
        graph = sub._per_owner_graph(vertices, fresh, unit_parsed, unit_changed, unit_removed, module_fields)
        return _UnitResult(graph, sub.report)

    def _unit_definitions(self, unit: str, parsed: dict[TFDefinitionKey, Any],
                          removed: set[TFDefinitionKey]) -> dict[TFDefinitionKey, Any]:
        definitions = {k: loads(v) for k, v in self.pickled_definitions.items()
                       if unit_of_key(k) == unit and k not in removed and k not in parsed}
        definitions.update({k: v for k, v in parsed.items() if unit_of_key(k) == unit})
        return definitions

    def _tfvar_source(self) -> list[Any]:
        new_blocks = getattr(self, "new_tfvar_blocks", None)
        return new_blocks if new_blocks is not None else [loads(t) for t in self.a["tfvar_blocks"]]

    def _tfvar_units(self) -> dict[tuple[str, str], str]:
        """(load_dir, name) -> unit the baseline placed that tfvar vertex in (the unit of the variable it feeds)."""
        placement: dict[tuple[str, str], str] = {}
        for index in self.a["tfvar_vertices"]:
            block = self._reused_vertex(index)
            placement[(str(block.attributes.get("load_dir")), block.name)] = self.a["unit_by_vertex"][index]
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
        self.touched_units = per_owner | scoped
        old_by_unit: dict[str, list[int]] = defaultdict(list)
        for index, unit in enumerate(self.a["unit_by_vertex"]):
            old_by_unit[unit].append(index)
        vertices: list[Any] = []
        new_index_of_old: dict[int, int] = {}
        for unit in sorted(old_by_unit):
            if unit in scoped or unit in per_owner:
                continue
            for old in old_by_unit[unit]:
                new_index_of_old[old] = len(vertices)
                vertices.append(self._reused_vertex(old))
        edges: list[tuple[int, int, str]] = []
        for origin, dest, label, _, _ in self.a["edges"]:
            if origin in new_index_of_old:
                edges.append((new_index_of_old[origin], new_index_of_old[dest], label))
        for old, new in new_index_of_old.items():
            vertex = vertices[new]
            vertex.source_module = {new_index_of_old[i] for i in self.a["source_module"][old]}
            vertex.module_connections = {attr: [new_index_of_old[i] for i in ids]
                                         for attr, ids in self.a["module_connections"][old].items()}
            if NEGATIVE_CONTROL == "no_index_field_restore":
                vertex.source_module, vertex.module_connections = set(), {}
        reused_vertices, reused_edges = len(vertices), len(edges)
        unit_reports: dict[str, Any] = {}
        for unit in sorted(per_owner):
            sub = self._per_owner_unit(unit, parsed, changed, removed, module_fields)
            offset = len(vertices)
            vertices.extend(sub.graph.vertices)
            for vertex in sub.graph.vertices:
                vertex.source_module = {i + offset for i in vertex.source_module}
                vertex.module_connections = {a: [i + offset for i in ids] for a, ids in vertex.module_connections.items()}
            edges.extend((e.origin + offset, e.dest + offset, e.label) for e in sub.graph.edges)
            reused_vertices += sub.report.vertices_reused
            reused_edges += sub.report.edges_reused
            unit_reports[unit] = {"mode": "per-owner", "vertices": sub.report.vertices,
                                  "vertices_rebuilt": sub.report.vertices_rebuilt, "edges": sub.report.edges,
                                  "edges_rebuilt": sub.report.edges_rebuilt,
                                  "edge_owners_rebuilt": sub.report.edge_owners_rebuilt}
        for unit in sorted(scoped):
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
            global_types, global_aliases = self._pr_global_tokens(parsed, removed)
            oracle = self._expansion_oracle()
            if unit not in reparsed_units and oracle is not None and instance_update_enabled():
                instance_result = self._instance_level_unit(unit, parsed, changed, removed, module_fields,
                                                            definitions, tfvars, global_types, global_aliases)
                if instance_result is not None:
                    sub, report = instance_result
                    offset = len(vertices)
                    vertices.extend(sub.graph.vertices)
                    for vertex in sub.graph.vertices:
                        vertex.source_module = {i + offset for i in vertex.source_module}
                        vertex.module_connections = {a: [i + offset for i in ids]
                                                     for a, ids in vertex.module_connections.items()}
                    edges.extend((e.origin + offset, e.dest + offset, e.label) for e in sub.graph.edges)
                    reused_vertices += sub.report.vertices_reused
                    reused_edges += sub.report.edges_reused
                    unit_reports[unit] = report
                    continue
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

    def _instance_level_unit(self, unit: str, parsed: dict[TFDefinitionKey, Any], changed: set[TFDefinitionKey],
                             removed: set[TFDefinitionKey], module_fields: dict[str, Any],
                             definitions: dict[TFDefinitionKey, Any], tfvars: list[Any], global_types: set[str],
                             global_aliases: set[tuple[str, str]]) -> Optional[tuple["_UnitResult", dict[str, Any]]]:
        """Round 8: a unit with count / for_each updated per block instead of rebuilt. Statements are decided on the
        unit's PRE-EXPANSION graph (vertices + edges as Checkov's first _build_edges pass leaves them): unchanged read
        closure -> baseline statement, else Checkov's own static / dynamic evaluation for those blocks only. Blocks
        whose creation state and statement are unchanged keep their baseline instances; the others are re-expanded
        with Checkov's instance code; the unit then goes through the per-owner edge engine. None -> the caller falls
        back to the whole-unit rebuild (module count / for_each, enabled data expansion, anything not reproducible)."""
        if any(_has_module_expansion(d) for d in definitions.values()):
            return None
        oracle = self._expansion_oracle()
        try:
            self._decide_unit_statements(definitions, tfvars, module_fields, global_types, global_aliases, oracle)
            sub = DiffEngine.__new__(DiffEngine)
            sub.__init__(self._unit_artifact(unit), self.root, self.changes)
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
        report = {"mode": "instance-level", "vertices": sub.report.vertices,
                  "vertices_rebuilt": sub.report.vertices_rebuilt, "edges": sub.report.edges,
                  "edges_rebuilt": sub.report.edges_rebuilt, "edge_owners_rebuilt": sub.report.edge_owners_rebuilt,
                  **splicer.stats, **self._expansion_report(oracle)}
        return _UnitResult(graph, sub.report), report

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
                "expansions_changed": sorted(_short_block(k) for k in oracle.changed)}

    def _assemble(self, vertices: list[Any], edges: list[tuple[int, int, str]], parsed: dict[TFDefinitionKey, Any],
                  removed: set[TFDefinitionKey], changed: set[TFDefinitionKey],
                  module_fields: dict[str, Any]) -> TerraformLocalGraph:
        module = Module(source_dir=module_fields["source_dir"],
                        external_modules_source_map=module_fields["external_modules_source_map"])
        module.source = module_fields["source"]
        module.blocks = vertices
        kept = {k: v for k, v in self.pickled_definitions.items() if k not in removed and k not in changed}
        module.temp_tf_definition = LazyDefinitions(kept, dict(parsed))
        module.resources_types = {t for k, d in self.definition_entries.items() if k in kept
                                  for t in d["resource_types"]} | {t for d in parsed.values()
                                                                   for t in resource_types_of(d)}
        graph = TerraformLocalGraph(module)
        graph.vertices = vertices
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
        touched = set(scoped) | set(getattr(self, "touched_units", set()))
        for index, vertex in enumerate(graph.vertices):
            if tokens and unit_of_vertex(vertex) not in touched and _mentions(vertex, tokens):
                raise IncrementalGraphUnsupported(
                    f"unchanged unit vertex {vertex.name} mentions an added/removed resource type or alias")
        # Scoped units are built with the PR-wide lookup lists (build_unit global_*): verify the assembled graph's own
        # lists equal the ones the units were built with, i.e. the precomputation from definitions was exact.
        types, aliases = self._pr_global_tokens(self._last_parsed, self._last_removed)
        if set(graph.get_resources_types_in_graph()) != types:
            raise IncrementalGraphUnsupported("global resource-type list of the assembled graph differs from the one "
                                              "scoped units were built with")
        if {(n, b) for n, b in aliases_signature(graph)} != aliases:
            raise IncrementalGraphUnsupported("global provider-alias list of the assembled graph differs from the one "
                                              "scoped units were built with")

    def _fill_scoped_report(self, graph: TerraformLocalGraph, reused_vertices: int, reused_edges: int,
                            unit_reports: dict[str, Any], changed: set[TFDefinitionKey], reparsed: int) -> None:
        r = self.report
        new_keys = vertex_keys(graph, self.root)
        old_set, new_set = set(self.old_keys), set(new_keys)
        r.definition_keys = len(graph.module.temp_tf_definition)
        r.definition_keys_reparsed = reparsed
        r.vertices = len(new_keys)
        r.vertices_reused = reused_vertices
        r.vertices_rebuilt = r.vertices - reused_vertices
        r.vertices_added = sorted(_short(k) for k in new_set - old_set)
        r.vertices_removed = sorted(_short(k) for k in old_set - new_set)
        r.edges = len(graph.edges)
        r.edges_reused = reused_edges
        r.edges_rebuilt = r.edges - reused_edges
        r.scoped_units = {os.path.relpath(u, self.root): v for u, v in unit_reports.items()}
        r.units_total = len(self.a["units"])
        r.units_reused = r.units_total - len([u for u in unit_reports if u in self.a["units"]])
        instances = {k.tf_source_modules for k in graph.module.temp_tf_definition.keys() if k.tf_source_modules}
        scoped_units = {u for u, v in unit_reports.items() if v.get("mode") == "scoped-rebuild"}
        updated = {k.tf_source_modules for k in graph.module.temp_tf_definition.keys()
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
        instances = {k.tf_source_modules for k in graph.module.temp_tf_definition.keys() if k.tf_source_modules}
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


