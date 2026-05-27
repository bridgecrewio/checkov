from __future__ import annotations

import importlib.util
import logging
import os
import sys
from importlib.abc import Loader, MetaPathFinder
from importlib.machinery import ModuleSpec
from types import ModuleType
from typing import Iterable, Mapping, Sequence


logger = logging.getLogger(__name__)


def _compile_and_exec_into_module(
    module: ModuleType, file_path: str, source_bytes: bytes, module_name: str,
) -> None:
    try:
        code = compile(source_bytes, file_path, "exec")
        exec(code, module.__dict__)
    except BaseException:
        sys.modules.pop(module_name, None)
        raise


def load_verified_sources_into_module(
    module_name: str,
    file_path: str,
    source_bytes: bytes,
) -> ModuleType:
    """Compile + exec ``source_bytes`` as ``module_name``.

    Pre-registers in ``sys.modules`` BEFORE exec so self-imports resolve.
    Cleans up on failure.
    """
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None:
        raise ImportError(f"cannot create module spec for {module_name} at {file_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    _compile_and_exec_into_module(module, file_path, source_bytes, module_name)
    return module


class _VerifiedSourceLoader(Loader):
    def __init__(self, file_path: str, source_bytes: bytes) -> None:
        self._file_path = file_path
        self._source_bytes = source_bytes

    def create_module(self, spec: ModuleSpec) -> "ModuleType | None":
        return None

    def exec_module(self, module: ModuleType) -> None:
        module.__dict__["__file__"] = self._file_path
        _compile_and_exec_into_module(
            module,
            self._file_path,
            self._source_bytes,
            getattr(module, "__name__", ""),
        )

    def get_source(self, fullname: str) -> str:
        return self._source_bytes.decode("utf-8", errors="replace")


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
                loader = _VerifiedSourceLoader(candidate_path, source_bytes)
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
    """Idempotent — second call is a silent no-op."""
    try:
        sys.meta_path.remove(finder)
    except ValueError:
        pass


__all__ = [
    "VerifiedSourcesFinder",
    "install_finder",
    "load_verified_sources_into_module",
    "uninstall_finder",
]
