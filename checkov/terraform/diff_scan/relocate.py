"""Artifact relocation: a baseline taken at /a/repo used by a PR scan at /b/repo.

Every absolute path in the artifact is under the baseline root (repository files, local modules, and external modules,
which the pre-scan materialises under <root>/.external_modules/). Relocation rewrites the root prefix everywhere:

  * plain JSON values      string replacement on path-like strings (exact root or root + separator)
  * pickled objects        unpickle, rewrite every str reachable through dicts / lists / tuples / sets / dataclasses
                           (TFModule, TFDefinitionKey, frozen) and __slots__ objects (TerraformBlock), re-pickle
  * the rendered export    already stores "<root>" placeholders (incremental_graph._anonymise); restored with the new
                           root by incremental_graph itself

Identity is repository-relative by construction: two roots that hold the same tree yield the same keys after
relocation (verified by the relocation scenarios: exact parity with a full scan at the new root).
"""
from __future__ import annotations

import dataclasses
import os
import pickle
from typing import Any

from checkov.terraform.diff_scan.artifact import dumps, loads

PICKLED_LIST_FIELDS = ("vertices", "tfvar_blocks")
PICKLED_FIELDS = ("module",)


class Relocator:
    """Rewrites the root prefix while PRESERVING OBJECT IDENTITY: mutable containers (dict / list / set) and
    __slots__ objects are rewritten in place, and every object is visited once (memo). Checkov's pre-render vertices
    alias nested values (e.g. attributes["dynamic.0"] IS attributes["dynamic"][0]) and its renderer writes through
    those aliases; copying containers would silently break that sharing and change rendering results.
    Immutable values (str, tuple, frozen dataclasses: TFModule / TFDefinitionKey) are rebuilt (memoised, so a shared
    immutable stays shared)."""

    def __init__(self, old_root: str, new_root: str) -> None:
        self.old = old_root.rstrip(os.sep)
        self.new = new_root.rstrip(os.sep)
        self.memo: dict[int, Any] = {}

    def text(self, value: str) -> str:
        if value == self.old:
            return self.new
        if self.old + os.sep in value:
            return value.replace(self.old + os.sep, self.new + os.sep)
        return value

    def value(self, value: Any) -> Any:
        if isinstance(value, str):
            return self.text(value)
        if value is None or isinstance(value, (int, float, bool, bytes)):
            return value
        key = id(value)
        if key in self.memo:
            return self.memo[key]
        if isinstance(value, dict):
            self.memo[key] = value
            items = list(value.items())
            value.clear()
            for k, v in items:
                value[self.value(k)] = self.value(v)
            return value
        if isinstance(value, list):
            self.memo[key] = value
            value[:] = [self.value(v) for v in value]
            return value
        if isinstance(value, set):
            self.memo[key] = value
            items = list(value)
            value.clear()
            value.update(self.value(v) for v in items)
            return value
        if isinstance(value, tuple):
            moved = tuple(self.value(v) for v in value)
            self.memo[key] = moved
            return moved
        if dataclasses.is_dataclass(value) and not isinstance(value, type):
            changes = {f.name: self.value(getattr(value, f.name)) for f in dataclasses.fields(value)}
            moved = dataclasses.replace(value, **changes)
            self.memo[key] = moved
            return moved
        slots = [s for cls in type(value).__mro__ for s in getattr(cls, "__slots__", ())]
        if slots:
            self.memo[key] = value
            for slot in slots:
                if hasattr(value, slot):
                    setattr(value, slot, self.value(getattr(value, slot)))
            return value
        return value

    def pickled(self, text: str | bytes) -> str | bytes:
        """Each pickle is one object graph: aliasing inside it is preserved (fresh memo per pickle). Keeps the input's
        form: base64 text (v2 JSON artifact) or raw pickle bytes (v3 section store)."""
        self.memo = {}
        if os.getenv("DFO_NEGATIVE") == "relocation_breaks_aliasing":
            moved = _copying_value(self, loads(text))
        else:
            moved = self.value(loads(text))
        return pickle.dumps(moved) if isinstance(text, bytes) else dumps(moved)


def _copying_value(r: Relocator, value: Any) -> Any:
    """Negative control: the first (buggy) relocator, which rebuilt containers and so broke aliasing."""
    if isinstance(value, str):
        return r.text(value)
    if isinstance(value, dict):
        return {_copying_value(r, k): _copying_value(r, v) for k, v in value.items()}
    if isinstance(value, list):
        return [_copying_value(r, v) for v in value]
    if isinstance(value, tuple):
        return tuple(_copying_value(r, v) for v in value)
    if isinstance(value, set):
        return {_copying_value(r, v) for v in value}
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return dataclasses.replace(value, **{f.name: _copying_value(r, getattr(value, f.name))
                                             for f in dataclasses.fields(value)})
    for slot in [s for cls in type(value).__mro__ for s in getattr(cls, "__slots__", ())]:
        if hasattr(value, slot):
            setattr(value, slot, _copying_value(r, getattr(value, slot)))
    return value


FAST_RELOCATION_ENV = "CHECKOV_DIFF_FAST_RELOCATION"


def fast_relocation_enabled() -> bool:
    """Opt-in: same relocated values, less work. A plain section none of whose strings contains the old root is
    returned untouched (Relocator.value only rewrites strings containing it); definition keys are relocated as
    objects, sharing each relocated TFModule chain, instead of unpickle -> rewrite -> re-pickle -> unpickle."""
    return os.getenv(FAST_RELOCATION_ENV, "false").lower() == "true"


def _mentions_root(value: Any, old_root: str) -> bool:
    """True if any str in `value` (dict keys included) contains `old_root`, or `value` holds anything other than
    plain JSON-like containers and scalars (then Relocator.value decides). Iterative, no copy, stops at the first hit."""
    stack = [value]
    while stack:
        item = stack.pop()
        if isinstance(item, str):
            if old_root in item:
                return True
        elif isinstance(item, dict):
            stack.extend(item.keys())
            stack.extend(item.values())
        elif isinstance(item, (list, tuple)):
            stack.extend(item)
        elif not (item is None or isinstance(item, (int, float, bool, bytes))):
            return True
    return False


class _KeyRelocator:
    """TFDefinitionKey / TFModule relocation by value: equal results to Relocator.pickled followed by loads, each
    distinct module chain rebuilt once."""

    def __init__(self, r: Relocator) -> None:
        self.r = r
        self.modules: dict[Any, Any] = {}

    def module(self, m: Any) -> Any:
        if m is None:
            return None
        moved = self.modules.get(m)
        if moved is None:
            moved = dataclasses.replace(m, path=self.r.text(m.path), nested_tf_module=self.module(m.nested_tf_module))
            self.modules[m] = moved
        return moved

    def key(self, stored: Any) -> Any:
        """`stored`: a pickled key, or a key already relocated by value (relocation runs before rename remapping)."""
        from checkov.terraform.modules.module_objects import TFDefinitionKey

        key = loads(stored) if isinstance(stored, (str, bytes)) else stored
        if type(key) is not TFDefinitionKey or type(key.tf_source_modules).__name__ not in ("TFModule", "NoneType"):
            return self.r.value(key)
        return dataclasses.replace(key, file_path=self.r.text(key.file_path),
                                   tf_source_modules=self.module(key.tf_source_modules))


def _relocate_section_fast(key: str, value: Any, r: Relocator) -> Any:
    from checkov.terraform.diff_scan.artifact_store import IndexedDefinitions

    if key == "definitions" and isinstance(value, IndexedDefinitions):
        keys = _KeyRelocator(r)
        moved = value.with_transform(lambda d: {**d, "key": keys.key(d["key"])}, r.pickled)
        keys.modules.clear()
        return moved
    if key in PICKLED_LIST_FIELDS or key in PICKLED_FIELDS or key in ("definitions", "alias_keys", "variable_inputs",
                                                                      "rendered", "baseline_inputs", "findings.meta",
                                                                      "findings.vertices"):
        return None
    if not _mentions_root(value, r.old):
        return value
    return None


def relocate_section(key: str, value: Any, r: Relocator) -> Any:
    """One artifact section valid at the relocator's new root."""
    from checkov.terraform.diff_scan.artifact_store import IndexedDefinitions, IndexedList

    if fast_relocation_enabled():
        fast = _relocate_section_fast(key, value, r)
        if fast is not None:
            return fast
    if key in PICKLED_LIST_FIELDS:
        if isinstance(value, IndexedList):
            return value.with_transform(r.pickled)
        return [r.pickled(v) for v in value]
    if key in PICKLED_FIELDS:
        return r.pickled(value)
    if key == "definitions":
        if isinstance(value, IndexedDefinitions):
            return value.with_transform(lambda d: {**d, "key": r.pickled(d["key"])}, r.pickled)
        return [{**d, "key": r.pickled(d["key"]), "definition": r.pickled(d["definition"])} for d in value]
    if key == "alias_keys":
        return {name: [r.pickled(k) for k in keys] for name, keys in value.items()}
    if key == "variable_inputs":
        return {**r.value({k: v for k, v in value.items() if k != "external_vars"}),
                "external_vars": r.pickled(value["external_vars"])}
    if key in ("rendered", "baseline_inputs", "findings.meta", "findings.vertices"):
        return value
    return r.value(value)


def relocate_artifact(artifact: Any, new_root: str) -> Any:
    """A copy of `artifact` valid at `new_root`. No-op when the roots are equal. A section store (ArtifactSections)
    relocates each section when it is decoded instead (relocate_on_load), so nothing is decoded up front."""
    old_root = artifact["root"]
    if os.path.realpath(old_root) == os.path.realpath(new_root):
        return artifact
    relocate_on_load = getattr(artifact, "relocate_on_load", None)
    if relocate_on_load is not None:
        root_free = getattr(artifact, "root_free_sections", frozenset()) if fast_relocation_enabled() else frozenset()
        if os.getenv("DFO_NEGATIVE", "") == "root_free_section_lies":
            root_free = root_free | {"files", "unit_by_vertex", "units"}

        def relocate(key: str, value: Any) -> Any:
            if key in root_free:
                return value
            return relocate_section(key, value, Relocator(old_root, new_root))

        relocate_on_load(relocate, new_root)
        return artifact
    r = Relocator(old_root, new_root)
    moved: dict[str, Any] = {key: relocate_section(key, value, r) for key, value in artifact.items()}
    moved["root"] = new_root
    moved["relocated_from"] = old_root
    return moved
