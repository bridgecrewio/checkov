"""Round 9 step 1b: a Terraform file added to / deleted from a directory loaded as a module, without re-parsing the
calling units.

Checkov resolves a module call by loading the directory's files in sorted order; the call's `__resolved__` lists one
definition key per loaded file, in that order, and it is part of the CALLER vertex's config. So adding / deleting a
file in a module directory changes:
  1. the module instance's blocks (the file's blocks appear / disappear in every instance), and
  2. every caller's `__resolved__` list (one entry added / removed).
(1) is what an edit of that file per instance already does (empty -> content / content -> empty); (2) is a pure
list edit. Both together equal Checkov's re-parse when the file is LAST in the directory's sorted order (verified:
`__resolved__` is the only other difference, the files before it keep their positions; doc/RENAME_POC_PLAN.md).
A file that is not last shifts the order of later files' blocks, which is observable (probe 1), so it keeps the
re-parse. Also kept: files whose blocks contain `module` calls (topology), variable files, new directories.

The patch is applied to the caller definitions (definitions section) and the caller vertices are recreated from
them by the regular per-owner path (a caller key in `parsed` is a changed key), so edges and rendering follow.
"""
from __future__ import annotations

import json
import os
from typing import Any, Optional

from checkov.common.util.consts import RESOLVED_MODULE_ENTRY_NAME
from checkov.common.util.data_structures_utils import pickle_deepcopy
from checkov.terraform.diff_scan.tfvars import is_terraform_file, is_variable_file
from checkov.terraform.modules.module_objects import TFDefinitionKey

MODULE_FILE_SET_ENV = "CHECKOV_DIFF_MODULE_FILE_SET"
"""Opt-in (set by the diff scan)."""

NEGATIVE_CONTROL = os.getenv("DFO_NEGATIVE", "")


def module_file_set_enabled() -> bool:
    return os.getenv(MODULE_FILE_SET_ENV, "false").lower() == "true"


def _module_calls(definition: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    return [(name, data) for call in definition.get("module", []) if isinstance(call, dict)
            for name, data in call.items() if isinstance(data, dict)]


def directory_files_after(stored_files: dict[str, Any], directory: str, added: set[str], deleted: set[str]) \
        -> list[str]:
    """Terraform files (not variable files) of `directory` as of the PR, in Checkov's load order (sorted)."""
    files = {p for p in stored_files if os.path.dirname(p) == directory and is_terraform_file(p)
             and not is_variable_file(p)}
    return sorted((files - deleted) | added)


def is_last(path: str, ordered: list[str]) -> bool:
    if NEGATIVE_CONTROL == "module_file_ignore_order":
        return True
    return bool(ordered) and ordered[-1] == path


class ModuleFileSetPlan:
    """Which module-directory file adds / deletes are handled per instance, and the caller definitions to patch."""

    def __init__(self, pickled_definitions: dict[TFDefinitionKey, Any], stored_files: dict[str, Any],
                 loads: Any) -> None:
        self.pickled = pickled_definitions
        self.files = stored_files
        self.loads = loads
        self.handled_directories: set[str] = set()
        self.refused: dict[str, str] = {}

    def decide(self, directories: set[str], added: dict[str, Any], deleted: set[str]) -> set[str]:
        """Directories whose file set change is handled here (no re-parse). `added`: path -> parsed definition of
        new files in loaded module directories; `deleted`: deleted files there."""
        if not module_file_set_enabled():
            return set()
        for directory in sorted(directories):
            new = {p for p in added if os.path.dirname(p) == directory}
            gone = {p for p in deleted if os.path.dirname(p) == directory}
            reason = self._refusal(directory, new, gone, added)
            if reason:
                self.refused[directory] = reason
            else:
                self.handled_directories.add(directory)
        return set(self.handled_directories)

    def _refusal(self, directory: str, new: set[str], gone: set[str], added: dict[str, Any]) -> Optional[str]:
        if len(new) + len(gone) != 1:
            return "more than one file added / deleted in the directory"
        path = next(iter(new | gone))
        if is_variable_file(path):
            return "variable file"
        definition = added.get(path) if new else self._stored_definition(path)
        if definition is None:
            return "no definition"
        if _module_calls(definition):
            return "file holds module calls (topology)"
        before = directory_files_after(self.files, directory, set(), set())
        after = directory_files_after(self.files, directory, new, gone)
        order = after if new else before
        if not is_last(path, order):
            return "file is not last in the directory's sorted order"
        return None

    def _stored_definition(self, path: str) -> Optional[dict[str, Any]]:
        for key, value in self.pickled.items():
            if key.file_path == path:
                return self.loads(value)
        return None

    def caller_patches(self, added: set[str], deleted: set[str]) -> dict[TFDefinitionKey, dict[str, Any]]:
        """Caller definition key -> definition with every call into a handled directory carrying the PR's
        `__resolved__` (entry for the added file appended / for the deleted file removed)."""
        patches: dict[TFDefinitionKey, dict[str, Any]] = {}
        for key, value in self.pickled.items():
            definition = None
            for name, data in _module_calls(self.loads(value)):
                resolved = data.get(RESOLVED_MODULE_ENTRY_NAME)
                if not resolved or not isinstance(resolved, list):
                    continue
                first = _as_key(resolved[0])
                if os.path.dirname(first.file_path) not in self.handled_directories:
                    continue
                if definition is None:
                    definition = pickle_deepcopy(self.loads(value))
                self._patch_call(definition, name, first, added, deleted)
            if definition is not None:
                patches[key] = definition
        return patches

    def _patch_call(self, definition: dict[str, Any], name: str, first: TFDefinitionKey, added: set[str],
                    deleted: set[str]) -> None:
        directory = os.path.dirname(first.file_path)
        for call_name, data in _module_calls(definition):
            if call_name != name:
                continue
            resolved = [_as_key(r) for r in data[RESOLVED_MODULE_ENTRY_NAME]]
            resolved = [r for r in resolved if r.file_path not in deleted]
            for path in sorted(p for p in added if os.path.dirname(p) == directory):
                resolved.append(TFDefinitionKey(file_path=path, tf_source_modules=first.tf_source_modules))
            data[RESOLVED_MODULE_ENTRY_NAME] = resolved


def _as_key(value: Any) -> TFDefinitionKey:
    return TFDefinitionKey.from_json(json.loads(value)) if isinstance(value, str) else value
