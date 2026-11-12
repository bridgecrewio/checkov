"""Restrict a stock runner's directory walk to a set of files, without changing the runner.

Every Checkov runner discovers files with `os.walk` (directly or via `get_scannable_file_paths`) and
filters them with `filter_ignored_paths`. Running with `root_folder` (not `files=`) keeps file paths,
resource ids and report layout byte-identical to a normal full scan; this module hides every file that
is not in the allowed set from that walk. The allowed set is the union of the selected units' files.

Implemented as a context manager that wraps `filter_ignored_paths` in every module that imported it,
so no runner code has to change.
"""
from __future__ import annotations

import os
import sys
from contextlib import contextmanager
from typing import Any, Iterable, Iterator

from checkov.common.runners import base_runner


@contextmanager
def only_files(root_folder: str, allowed_files: Iterable[str]) -> Iterator[None]:
    root = os.path.abspath(root_folder)
    allowed = {os.path.normpath(os.path.join(root, f)) for f in allowed_files}
    allowed_dirs = {root}
    for path in allowed:
        parent = os.path.dirname(path)
        while parent.startswith(root) and parent not in allowed_dirs:
            allowed_dirs.add(parent)
            parent = os.path.dirname(parent)

    original = base_runner.filter_ignored_paths

    def scoped_filter(root_dir: str, names: Any, excluded_paths: Any, included_paths: Any = None) -> None:
        original(root_dir, names, excluded_paths, included_paths)
        root_abs = os.path.abspath(str(root_dir))
        if os.path.commonpath([root, root_abs]) != root:
            # walks outside the scanned repo (e.g. Helm renders charts into a temp dir) are not scoped
            return
        for entry in list(names):
            name = str(entry.name) if isinstance(entry, os.DirEntry) else str(entry)
            full = os.path.normpath(os.path.join(root_abs, name))
            if full not in allowed and full not in allowed_dirs:
                names.remove(entry)

    patched = []
    for module in list(sys.modules.values()):
        if module is not None and getattr(module, "filter_ignored_paths", None) is original:
            module.filter_ignored_paths = scoped_filter  # type: ignore[attr-defined]
            patched.append(module)

    # Bicep discovers files with Path.rglob instead of os.walk + filter_ignored_paths
    import checkov.bicep.runner as bicep_runner
    original_bicep_scan = bicep_runner.get_scannable_file_paths

    def scoped_bicep_scan(*args: Any, **kwargs: Any) -> Any:
        return {p for p in original_bicep_scan(*args, **kwargs)
                if os.path.normpath(os.path.abspath(str(p))) in allowed}

    bicep_runner.get_scannable_file_paths = scoped_bicep_scan  # type: ignore[assignment]
    try:
        yield
    finally:
        for module in patched:
            module.filter_ignored_paths = original  # type: ignore[attr-defined]
        bicep_runner.get_scannable_file_paths = original_bicep_scan  # type: ignore[assignment]
