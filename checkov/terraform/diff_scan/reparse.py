"""Scoped unit re-parse for changes that alter WHICH definition keys exist (Phase B).

Used when a changed unit's key set cannot be derived from the baseline: a module call added / removed / re-sourced,
a new directory (new unit), a directory whose "called by some module" status flips, or a changed variable input.

Checkov's own TFParser runs on a VIRTUAL TREE in scratch (outside the repository), rooted at the unit's directory, so
that the parser walks only that directory (sub-directories that are units of their own are excluded):
  * the unit root directory's files            stored content (unchanged) / PR content (changed)
  * every local module directory it reaches    same, discovered iteratively from the module calls
  * external modules                           the pre-scan's materialised copies (never the repository)
Paths in the result are mapped back to repository paths. Only the unit's keys are kept.
Correctness rests on probe (a) in the PoC's doc/STATUS.md: a parse rooted at one unit gives that unit's keys from the full parse.
"""
from __future__ import annotations

import os
import shutil
from typing import Any, Optional

from checkov.terraform.modules.module_objects import TFDefinitionKey, TFModule
from checkov.terraform.tf_parser import TFParser


class VirtualTree:
    def __init__(self, scratch: str, root: str, files: dict[str, list[str]]) -> None:
        """`files`: repository path -> lines (stored contents updated with the PR's changed files)."""
        self.scratch = scratch
        self.root = root
        self.files = files

    def local(self, path: str) -> str:
        return os.path.join(self.scratch, os.path.relpath(path, self.root))

    def repo(self, path: str) -> str:
        if path.startswith(self.scratch + os.sep) or path == self.scratch:
            return os.path.normpath(os.path.join(self.root, os.path.relpath(path, self.scratch)))
        return path

    def materialise(self, directories: set[str]) -> None:
        shutil.rmtree(self.scratch, ignore_errors=True)
        os.makedirs(self.scratch)
        for path, lines in self.files.items():
            if os.path.dirname(path) in directories:
                local = self.local(path)
                os.makedirs(os.path.dirname(local), exist_ok=True)
                with open(local, "w") as f:
                    f.writelines(lines)


def _map_module(module: Optional[TFModule], tree: VirtualTree) -> Optional[TFModule]:
    if module is None:
        return None
    return TFModule(path=tree.repo(module.path), name=module.name,
                    nested_tf_module=_map_module(module.nested_tf_module, tree), foreach_idx=module.foreach_idx)


def _map_key(key: TFDefinitionKey, tree: VirtualTree) -> TFDefinitionKey:
    return TFDefinitionKey(file_path=tree.repo(key.file_path), tf_source_modules=_map_module(key.tf_source_modules, tree))


def _map_value(value: Any, tree: VirtualTree) -> Any:
    if isinstance(value, TFDefinitionKey):
        return _map_key(value, tree)
    if isinstance(value, dict):
        return {k: _map_value(v, tree) for k, v in value.items()}
    if isinstance(value, list):
        return [_map_value(v, tree) for v in value]
    if isinstance(value, str) and tree.scratch in value:
        return value.replace(tree.scratch, tree.root)
    return value


def parse_unit(unit_dir: str, tree: VirtualTree, module_dirs: set[str], excluded: list[str],
               external_modules: dict[str, Any], var_files: Optional[list[str]]) -> tuple[dict[TFDefinitionKey, Any],
                                                                                       dict[str, Any]]:
    """Definitions of one unit and the parser's external_vars, both with repository paths.
    `module_dirs`: local module directories the unit may load (materialised next to it). `excluded`: sub-directories
    of the unit root that are separate units (not walked)."""
    tree.materialise({unit_dir} | module_dirs)
    for directory in excluded:
        shutil.rmtree(tree.local(directory), ignore_errors=True)
    parser = TFParser()
    _, definitions = parser.parse_hcl_module(
        tree.local(unit_dir), "terraform", download_external_modules=False,
        external_modules_content_cache=external_modules,
        vars_files=[tree.local(v) for v in var_files or []] or None)
    mapped = {_map_key(k, tree): _map_value(v, tree) for k, v in definitions.items()}
    external_vars = {tree.repo(d): {n: (v, tree.repo(s)) for n, (v, s) in names.items()}
                     for d, names in parser.external_vars.items()}
    source_map = {address: tree.repo(path) for address, path in parser.external_modules_source_map.items()}
    return mapped, {"external_vars": external_vars, "external_modules_source_map": source_map}
