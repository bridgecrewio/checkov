"""Variable inputs (tfvars, --var-file, TF_VAR_*) for diff-files-only scans.

Checkov's parser runs TFParser.handle_variables once per directory it loads, in parser order. Each call builds
external_vars[dir] from: TF_VAR_* env < terraform.tfvars < terraform.tfvars.json < *.auto.tfvars(.json) < --var-file,
minus the variables a module call sets explicitly (`specified_vars`). add_tfvars then creates one `tfvar` block per
(dir, name). The first call that produces anything for a directory wins.

Baseline: record each call (directory, the variable files present in it, specified_vars) and the parser's final
external_vars. PR scan: replay the same calls with Checkov's own handle_variables, using stored contents for unchanged
variable files and the PR's contents for changed ones, plus the PR's TF_VAR_* env and --var-file. The resulting tfvar
blocks are diffed against the baseline's; only the units owning a changed `load_dir` are touched.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Callable, Optional

from checkov.terraform.graph_builder.graph_components.block_types import BlockType
from checkov.terraform.graph_builder.graph_components.module import Module
from checkov.terraform.tf_parser import TFParser

VARIABLE_FILE_SUFFIXES = (".tfvars", ".tfvars.json")
TERRAFORM_FILE_SUFFIXES = (".tf", ".hcl")
"""Files Checkov's directory scan loads as Terraform (TFParser.handle_variables collects .tf and .hcl)."""
IGNORED_BY_CHECKOV_SUFFIXES = (".tf.json",)
"""Files Checkov's directory scan never loads (handle_variables: "TODO: add support for .tf.json"). A change to one
cannot change a full scan, so the diff scan accepts and records it, and it contributes nothing."""


def is_terraform_file(path: str) -> bool:
    return path.endswith(TERRAFORM_FILE_SUFFIXES)


def is_ignored_by_checkov(path: str) -> bool:
    return path.endswith(IGNORED_BY_CHECKOV_SUFFIXES)


def is_variable_file(path: str) -> bool:
    return path.endswith(VARIABLE_FILE_SUFFIXES)


@dataclass
class HandleVariablesCall:
    directory: str
    specified_vars: Optional[dict[str, Any]]


def record_calls(parser: TFParser) -> tuple[list[HandleVariablesCall], dict[str, str], Callable[[], None]]:
    """Wrap parser.handle_variables to record every call and the variable files it saw.
    Returns (calls, variable file path -> text, uninstall)."""
    calls: list[HandleVariablesCall] = []
    files: dict[str, str] = {}
    original = parser.handle_variables

    def recording(dir_contents: list[os.DirEntry[str]], vars_files: Any, specified_vars: Any) -> list[str]:
        if dir_contents:
            calls.append(HandleVariablesCall(os.path.dirname(dir_contents[0].path),
                                             dict(specified_vars) if specified_vars else None))
            for entry in dir_contents:
                if _is_file(entry) and is_variable_file(entry.name) and entry.path not in files:
                    with open(entry.path, encoding="utf-8-sig") as f:
                        files[entry.path] = f.read()
        return original(dir_contents, vars_files, specified_vars)

    parser.handle_variables = recording  # type: ignore[method-assign]
    return calls, files, lambda: vars(parser).pop("handle_variables", None)


def _is_file(entry: os.DirEntry[str]) -> bool:
    try:
        return entry.is_file()
    except OSError:
        return False


class _Entry:
    """os.DirEntry stand-in for a stored file (only .name / .path / .is_file() are read)."""

    def __init__(self, path: str) -> None:
        self.path = path
        self.name = os.path.basename(path)

    def is_file(self) -> bool:
        return True


class _DirMarker:
    """First directory entry: Checkov keys external_vars by dirname(dir_contents[0].path); it is not a file."""

    def __init__(self, directory: str) -> None:
        self.path = os.path.join(directory, "__directory__")
        self.name = "__directory__"

    @staticmethod
    def is_file() -> bool:
        return False


def replay(calls: list[HandleVariablesCall], contents: dict[str, str], var_files: Optional[list[str]],
           scratch: str) -> dict[str, dict[str, tuple[Any, str]]]:
    """Checkov's own handle_variables replayed over the recorded calls.

    `contents`: variable file path -> text (stored for unchanged files, PR content for changed ones; a deleted file is
    absent). Checkov's loaders need real files, so contents are materialised under `scratch` (outside the repository);
    the source paths Checkov reports are mapped back to repository paths. The directory key stays the repository
    directory (the marker entry sits there and is never opened)."""
    parser = TFParser()
    parser.out_parsing_errors = {}
    parser.env_vars = dict(os.environ)
    mapping: dict[str, str] = {}
    for path, text in contents.items():
        local = os.path.join(scratch, path.lstrip(os.sep))
        os.makedirs(os.path.dirname(local), exist_ok=True)
        with open(local, "w") as f:
            f.write(text)
        mapping[local] = path
    reverse = {repo: local for local, repo in mapping.items()}
    local_var_files = [reverse.get(v, v) for v in var_files or []]
    for call in calls:
        files = [path for path in sorted(reverse) if os.path.dirname(path) == call.directory
                 and not any(path == v for v in var_files or [])]
        entries: list[Any] = [_DirMarker(call.directory)] + [_Entry(reverse[p]) for p in files]
        for entry, repo in zip(entries[1:], files):
            entry.name = os.path.basename(repo)
        parser.handle_variables(entries, local_var_files, call.specified_vars)
    return {d: {name: (value, mapping.get(src, src)) for name, (value, src) in names.items()}
            for d, names in parser.external_vars.items()}


def tfvar_blocks(external_vars: dict[str, dict[str, tuple[Any, str]]], source: str) -> list[Any]:
    """The tfvar blocks TFParser.add_tfvars creates for these external vars (same order)."""
    module = Module(source_dir="", external_modules_source_map={})
    for load_dir, names in external_vars.items():
        for name, (default, path) in names.items():
            module.add_blocks(BlockType.TF_VARIABLE, [{name: {"default": default, "load_dir": load_dir}}], path,
                              source)
    return module.blocks
