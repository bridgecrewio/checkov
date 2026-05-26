"""In-memory loader for verified external-check source bytes.

Exposes a :class:`VerifiedSourcesFinder` that, while installed on
:data:`sys.meta_path`, intercepts every ``import`` whose target file
sits inside one of the verified directories and serves its source from
the in-memory ``verified_sources`` allowlist instead of re-reading the
file from disk.

The invariant the finder enforces: **the bytes the verifier hashed are
the bytes the interpreter executes**. This holds for transitive imports
as well — e.g. a signed ``aws_check.py`` that does ``import _helper``
resolves through this finder and runs the verified in-memory bytes.
"""
from __future__ import annotations

import importlib.util
import logging
import os
import sys
from importlib.abc import Loader, MetaPathFinder
from importlib.machinery import ModuleSpec
from typing import Iterable, Mapping, Sequence


logger = logging.getLogger(__name__)


def load_verified_sources_into_module(
    module_name: str,
    file_path: str,
    source_bytes: bytes,
) -> "object":
    """Compile ``source_bytes`` and exec into a fresh module named ``module_name``.

    Registers the module in :data:`sys.modules` BEFORE executing so
    ``import module_name`` from inside ``source_bytes`` resolves to the
    in-flight module. ``file_path`` is set as ``module.__file__`` and is
    the filename argument to :func:`compile` so tracebacks point at the
    on-disk file even though the bytes came from memory.
    """
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None:
        raise ImportError(f"cannot create module spec for {module_name} at {file_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        code = compile(source_bytes, file_path, "exec")
        exec(code, module.__dict__)
    except BaseException:
        # Clean up a half-initialised module so it can't be re-used.
        sys.modules.pop(module_name, None)
        raise
    return module


class _VerifiedSourceLoader(Loader):
    """Loader that execs already-verified bytes; never touches disk."""

    def __init__(self, file_path: str, source_bytes: bytes) -> None:
        self._file_path = file_path
        self._source_bytes = source_bytes

    def create_module(self, spec: ModuleSpec) -> "object | None":
        return None

    def exec_module(self, module: "object") -> None:
        code = compile(self._source_bytes, self._file_path, "exec")
        module.__dict__["__file__"] = self._file_path  # type: ignore[attr-defined]
        exec(code, module.__dict__)  # type: ignore[attr-defined]

    def get_source(self, fullname: str) -> str:
        return self._source_bytes.decode("utf-8", errors="replace")


class VerifiedSourcesFinder(MetaPathFinder):
    """Meta-path finder that serves verified .py files from an in-memory map.

    v1 scope: only top-level (un-dotted) module names. The existing
    ``BaseCheckRegistry.load_external_checks`` flow imports each ``.py``
    by bare stem, so per-file resolution is sufficient. Packages of
    checks are out of scope for v1.
    """

    def __init__(
        self,
        verified_sources: Mapping[str, bytes],
        verified_dirs: Sequence[str],
    ) -> None:
        self._verified_sources = dict(verified_sources)
        self._verified_dirs = tuple(verified_dirs)

    def find_spec(
        self,
        fullname: str,
        path: "Sequence[str] | None" = None,
        target: "object | None" = None,
    ) -> "ModuleSpec | None":
        if "." in fullname:
            return None
        candidate_name = fullname.split(".")[-1] + ".py"
        for verified_dir in self._verified_dirs:
            candidate_path = os.path.join(verified_dir, candidate_name)
            if candidate_path in self._verified_sources:
                source_bytes = self._verified_sources[candidate_path]
                loader = _VerifiedSourceLoader(candidate_path, source_bytes)
                return importlib.util.spec_from_loader(fullname, loader, origin=candidate_path)
        return None


def install_finder(
    verified_sources: Mapping[str, bytes],
    verified_dirs: Iterable[str],
) -> VerifiedSourcesFinder:
    """Install a :class:`VerifiedSourcesFinder` at the front of ``sys.meta_path``."""
    finder = VerifiedSourcesFinder(verified_sources, list(verified_dirs))
    sys.meta_path.insert(0, finder)
    return finder


def uninstall_finder(finder: VerifiedSourcesFinder) -> None:
    """Remove ``finder`` from :data:`sys.meta_path`. Idempotent."""
    try:
        sys.meta_path.remove(finder)
    except ValueError:
        logger.debug("verified-sources finder was already absent from sys.meta_path")


__all__ = [
    "VerifiedSourcesFinder",
    "install_finder",
    "load_verified_sources_into_module",
    "uninstall_finder",
]
