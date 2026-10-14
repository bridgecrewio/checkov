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

    def pickled(self, text: str) -> str:
        """Each pickle is one object graph: aliasing inside it is preserved (fresh memo per pickle)."""
        self.memo = {}
        if os.getenv("DFO_NEGATIVE") == "relocation_breaks_aliasing":
            return dumps(_copying_value(self, loads(text)))
        return dumps(self.value(loads(text)))


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


def relocate_artifact(artifact: dict[str, Any], new_root: str) -> dict[str, Any]:
    """A copy of `artifact` valid at `new_root`. No-op when the roots are equal."""
    old_root = artifact["root"]
    if os.path.realpath(old_root) == os.path.realpath(new_root):
        return artifact
    r = Relocator(old_root, new_root)
    moved: dict[str, Any] = {}
    for key, value in artifact.items():
        if key in PICKLED_LIST_FIELDS:
            moved[key] = [r.pickled(v) for v in value]
        elif key in PICKLED_FIELDS:
            moved[key] = r.pickled(value)
        elif key == "definitions":
            moved[key] = [{**d, "key": r.pickled(d["key"]), "definition": r.pickled(d["definition"])} for d in value]
        elif key == "alias_keys":
            moved[key] = {name: [r.pickled(k) for k in keys] for name, keys in value.items()}
        elif key == "variable_inputs":
            moved[key] = {**r.value({k: v for k, v in value.items() if k != "external_vars"}),
                          "external_vars": r.pickled(value["external_vars"])}
        elif key == "rendered":
            moved[key] = value
        else:
            moved[key] = r.value(value)
    moved["root"] = new_root
    moved["relocated_from"] = old_root
    return moved
