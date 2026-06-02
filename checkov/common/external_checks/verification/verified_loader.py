from __future__ import annotations

import importlib.util
import logging
import os
import sys
from importlib.abc import MetaPathFinder
from importlib.machinery import ModuleSpec, SourceFileLoader
from types import ModuleType
from typing import Iterable, Mapping, Sequence


logger = logging.getLogger(__name__)


class _VerifiedSourceLoader(SourceFileLoader):
    """Serves pre-verified in-memory bytes through the stdlib import machinery."""

    def __init__(self, fullname: str, file_path: str, source_bytes: bytes) -> None:
        super().__init__(fullname, file_path)
        self._source_bytes = source_bytes

    def get_data(self, path: str) -> bytes:
        return self._source_bytes

    def path_stats(self, path: str) -> "Mapping[str, int]":
        # Fixed mtime/size so the stdlib does not stat() the file or consult
        # an on-disk .pyc cache (which would not be re-verified).
        return {"mtime": 0, "size": len(self._source_bytes)}

    def get_source(self, fullname: str) -> str:
        return self._source_bytes.decode("utf-8", errors="replace")

    def set_data(  # type: ignore[override]
        self, path: str, data: bytes, *, _mode: int = 0o666,
    ) -> None:
        # Opt out of stdlib .pyc cache writes: those bytes would have no
        # trailer of their own and could be picked up by a later process.
        return None

    def exec_module(self, module: ModuleType) -> None:
        # Drop the half-initialised module on failure so a subsequent import
        # of the same name gets ModuleNotFoundError instead of a partial.
        try:
            super().exec_module(module)
        except BaseException:
            sys.modules.pop(module.__name__, None)
            raise


def load_verified_sources_into_module(
    module_name: str,
    file_path: str,
    source_bytes: bytes,
) -> ModuleType:
    """Load ``source_bytes`` as ``module_name`` via the stdlib import machinery.

    Pre-registers in ``sys.modules`` BEFORE ``exec_module`` so self-imports
    resolve. Cleans up on failure.
    """
    loader = _VerifiedSourceLoader(module_name, file_path, source_bytes)
    spec = importlib.util.spec_from_loader(module_name, loader, origin=file_path)
    if spec is None:
        raise ImportError(f"cannot create module spec for {module_name} at {file_path}")
    module = importlib.util.module_from_spec(spec)
    # spec_from_loader doesn't propagate __file__ onto the module; external
    # checks rely on it for diagnostics, so set it explicitly.
    module.__file__ = file_path
    sys.modules[module_name] = module
    try:
        loader.exec_module(module)
    except BaseException:
        sys.modules.pop(module_name, None)
        raise
    return module


class VerifiedSourcesFinder(MetaPathFinder):
    """v1 scope: top-level (un-dotted) module names only."""

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
        candidate_name = fullname + ".py"
        for verified_dir in self._verified_dirs:
            candidate_path = os.path.join(verified_dir, candidate_name)
            if candidate_path in self._verified_sources:
                source_bytes = self._verified_sources[candidate_path]
                loader = _VerifiedSourceLoader(fullname, candidate_path, source_bytes)
                return importlib.util.spec_from_loader(fullname, loader, origin=candidate_path)
        return None


def install_finder(
    verified_sources: Mapping[str, bytes],
    verified_dirs: Iterable[str],
) -> VerifiedSourcesFinder:
    finder = VerifiedSourcesFinder(verified_sources, list(verified_dirs))
    sys.meta_path.insert(0, finder)
    return finder


def uninstall_finder(finder: VerifiedSourcesFinder) -> None:
    """Idempotent — second call is a silent no-op.

    Uses identity-based removal (``x is not finder``) instead of
    ``sys.meta_path.remove(finder)``. ``list.remove`` is ``__eq__``-based
    and walks every element until it finds a match; if any earlier
    MetaPathFinder on ``sys.meta_path`` has a user-defined ``__eq__``
    that hangs (e.g. waiting on a lock held by another thread), the
    whole removal hangs with it. Filtering by ``is`` avoids any
    ``__eq__`` invocation. We rebuild the list in place so any other
    references to ``sys.meta_path`` keep seeing the same list object.
    """
    sys.meta_path[:] = [x for x in sys.meta_path if x is not finder]


__all__ = [
    "VerifiedSourcesFinder",
    "install_finder",
    "load_verified_sources_into_module",
    "uninstall_finder",
]
