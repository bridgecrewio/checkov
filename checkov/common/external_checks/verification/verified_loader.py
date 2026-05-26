"""In-memory loader for verified external-check source bytes.

This module exposes a ``MetaPathFinder`` that, while active on
``sys.meta_path``, intercepts every Python ``import`` whose target file
sits inside one of the verified external-checks directories and serves
its source from the in-memory ``verified_sources`` allowlist instead of
re-reading the file from disk.

This closes the TOCTOU window between the verifier's hash and the
loader's ``exec`` for **transitive** imports (e.g. a signed
``aws_check.py`` does ``import _helper``; without this finder Python's
default ``FileFinder`` re-reads ``_helper.py`` from disk and an attacker
who swapped the bytes between verify and import would get their code
executed). Direct loads via :func:`load_verified_sources_into_module`
also use the in-memory bytes for the same reason.

The finder is installed only for the duration of the load — see
:func:`install_finder` and the context-manager pattern in
``base_check_registry.load_external_checks``. Outside that window the
finder is uninstalled so it cannot interfere with the rest of the
Python program's imports.
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

    Returns the executed module object. Registers the module in
    :data:`sys.modules` under ``module_name`` before executing so that
    ``import module_name`` from inside ``source_bytes`` resolves to the
    in-flight module (the Python convention).

    ``file_path`` is set as ``module.__file__`` and used as the filename
    argument to :func:`compile` — tracebacks therefore point at the
    on-disk file even though the bytes came from memory.
    """
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None:
        raise ImportError(
            f"cannot create module spec for {module_name} at {file_path}"
        )
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        code = compile(source_bytes, file_path, "exec")
        exec(code, module.__dict__)
    except BaseException:
        # Clean up on failure so a half-initialised module can't be
        # re-used by a subsequent import attempt.
        sys.modules.pop(module_name, None)
        raise
    return module


class _VerifiedSourceLoader(Loader):
    """Loader that execs already-verified bytes; never touches disk."""

    def __init__(self, file_path: str, source_bytes: bytes) -> None:
        self._file_path = file_path
        self._source_bytes = source_bytes

    def create_module(self, spec: ModuleSpec) -> "object | None":
        return None  # use the default module-object construction

    def exec_module(self, module: "object") -> None:
        code = compile(self._source_bytes, self._file_path, "exec")
        # ``module.__dict__`` is the namespace exec writes into; pass
        # ``__file__`` so the executed code can introspect itself.
        module.__dict__["__file__"] = self._file_path  # type: ignore[attr-defined]
        exec(code, module.__dict__)  # type: ignore[attr-defined]

    def get_source(self, fullname: str) -> str:
        # Used by ``inspect.getsource`` and tracebacks. Decode as UTF-8
        # with replacement; the trailer-stripped bytes are pure code,
        # so decode errors here would indicate a corrupted allowlist.
        return self._source_bytes.decode("utf-8", errors="replace")


class VerifiedSourcesFinder(MetaPathFinder):
    """Meta-path finder that serves verified .py files from an in-memory map.

    Resolution algorithm for an ``import some_name`` request:

    1. For each verified directory the finder was constructed with
       (in iteration order), look for ``<dir>/<some_name>.py``.
    2. If that path is present in ``verified_sources``, return a
       ``ModuleSpec`` whose loader replays the in-memory bytes.
    3. Otherwise return ``None`` so the next finder on
       :data:`sys.meta_path` (typically the default ``PathFinder``)
       handles the import.

    This finder does **not** handle package imports (no ``__init__.py``
    sub-package traversal); the existing
    ``BaseCheckRegistry.load_external_checks`` flow imports each ``.py``
    file as a top-level module name, so per-file resolution is
    sufficient. Packages of checks are out of scope for v1.
    """

    def __init__(
        self,
        verified_sources: Mapping[str, bytes],
        verified_dirs: Sequence[str],
    ) -> None:
        # Keep an immutable snapshot — caller may mutate later.
        self._verified_sources = dict(verified_sources)
        self._verified_dirs = tuple(verified_dirs)

    def find_spec(
        self,
        fullname: str,
        path: "Sequence[str] | None" = None,
        target: "object | None" = None,
    ) -> "ModuleSpec | None":
        # Only consider top-level names; nested package paths are out
        # of scope for v1 per the module docstring.
        if "." in fullname:
            return None
        candidate_name = fullname.split(".")[-1] + ".py"
        for verified_dir in self._verified_dirs:
            candidate_path = os.path.join(verified_dir, candidate_name)
            if candidate_path in self._verified_sources:
                source_bytes = self._verified_sources[candidate_path]
                loader = _VerifiedSourceLoader(candidate_path, source_bytes)
                return importlib.util.spec_from_loader(
                    fullname,
                    loader,
                    origin=candidate_path,
                )
        return None


def install_finder(
    verified_sources: Mapping[str, bytes],
    verified_dirs: Iterable[str],
) -> VerifiedSourcesFinder:
    """Install a :class:`VerifiedSourcesFinder` at the front of ``sys.meta_path``.

    Returns the finder instance so the caller can pass it to
    :func:`uninstall_finder` once the load window closes.
    """
    finder = VerifiedSourcesFinder(verified_sources, list(verified_dirs))
    sys.meta_path.insert(0, finder)
    return finder


def uninstall_finder(finder: VerifiedSourcesFinder) -> None:
    """Remove ``finder`` from :data:`sys.meta_path` if it is still present.

    Idempotent: safe to call even if the finder was never installed or
    was already removed (e.g. by a test that manipulated
    :data:`sys.meta_path` directly).
    """
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
