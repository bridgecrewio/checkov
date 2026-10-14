"""Scan inputs that are not repository files: --var-file list and the pre-scan's resolved external modules."""
from __future__ import annotations

import os
import re
import shutil
from typing import Any, Optional

VAR_FILES_ENV = "DFO_VAR_FILES"
"""Comma-separated --var-file paths relative to the scanned root."""
MODULE_STORE_ENV = "DFO_MODULE_STORE"
"""External modules 'upstream' store (the pre-scan's clones)."""
MATERIALIZED_DIR = ".external_modules"
"""Where the pre-scan extracts every external module, as in production (apps/scanner-iac PrivateGitLoader extracts into
module_params.dest_dir = <root>/.external_modules/<source>): a stable path, identical for the baseline and PR scans.
These are pre-scan inputs, not repository files."""
EXTERNAL_MODULES_MANIFEST = "manifest.txt"
"""<store>/manifest.txt: one '<source>@<version>' per line (the pre-scan's resolved module list)."""


def source_slug(source: str) -> str:
    """Filesystem-safe directory name for a module source (pre-scan store layout)."""
    return re.sub(r"[^A-Za-z0-9._-]+", "_", source).strip("_")


def var_files_from_env(root: str) -> Optional[list[str]]:
    names = [n for n in os.getenv(VAR_FILES_ENV, "").split(",") if n]
    return [os.path.join(root, n) for n in names] or None


def external_modules(root: str) -> dict[str, Any]:
    """The pre-scan's resolved external modules, keyed "<source>:<version>" as Checkov's module loader expects.
    Every scan gets ALL of them (changed or not), materialised outside the repository tree; the list comes from the
    store manifest, never from scanning repository files."""
    store = os.getenv(MODULE_STORE_ENV)
    if not store:
        return {}
    from checkov.terraform.module_loading.content import ModuleContent

    with open(os.path.join(store, EXTERNAL_MODULES_MANIFEST)) as f:
        addresses = [line.strip() for line in f if line.strip()]
    materialized = os.path.join(root, MATERIALIZED_DIR)
    shutil.rmtree(materialized, ignore_errors=True)
    content: dict[str, Any] = {}
    for address in addresses:
        source, version = address.rsplit("@", 1)
        snapshot = os.path.join(store, "_sources", source_slug(source), version)
        destination = os.path.join(materialized, source_slug(source), version)
        shutil.copytree(snapshot, destination)
        content[f"{source}:{version}"] = ModuleContent(destination)
    return content


def is_external_module_path(path: str, root: str) -> bool:
    return path.startswith(os.path.join(root, MATERIALIZED_DIR) + os.sep)
