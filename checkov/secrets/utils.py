from __future__ import annotations

import os
import re
from collections.abc import Iterable

from checkov.common.runners.base_runner import ignored_directories, safe_remove
from checkov.common.util.consts import DEFAULT_EXTERNAL_MODULES_DIR

EXCLUDED_PATHS = [*ignored_directories, DEFAULT_EXTERNAL_MODULES_DIR, ".idea", ".git", "venv"]


def filter_excluded_paths(
    root_dir: str,
    names: list[str] | list[os.DirEntry[str]],
    excluded_paths: Iterable[str] | None,
) -> None:
    """Special build of checkov.common.runners.base_runner.filter_ignored_paths for Secrets scanning"""

    # support for the --skip-path flag
    if excluded_paths:
        compiled = []
        for p in excluded_paths:
            try:
                compiled.append(re.compile(p.replace(".terraform", r"\.terraform")))
            except re.error:
                # do not add compiled paths that aren't regexes
                continue
        for entry in list(names):
            path = entry.name if isinstance(entry, os.DirEntry) else entry
            full_path = os.path.join(root_dir, path)
            if any(pattern.search(full_path) for pattern in compiled) or any(p in full_path for p in excluded_paths):
                safe_remove(names, entry)

    # support for our own excluded paths list
    for entry in list(names):
        path = entry.name if isinstance(entry, os.DirEntry) else entry
        if path in EXCLUDED_PATHS:
            safe_remove(names, entry)
