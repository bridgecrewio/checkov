"""Directory-tree enforcement of signature verification.

This is the module the CLI chokepoint calls. It walks every configured
external-checks directory, identifies every Python-loadable file the
Python import machinery could reach from inside that tree, and requires
each one to be signed by one of the configured keys.

The verifier and the loader **must** share this enumeration (Phase 2).
The dict this function returns is the allowlist the loader consumes.
"""
from __future__ import annotations

import logging
import os
from typing import Iterable

from .keys import SignatureVerificationError, VerificationKey
from .signature_format import SIG_SUFFIX, sidecar_path_for
from .verifier import VerificationResult, verify_file_with_bytes


logger = logging.getLogger(__name__)


# Python file extensions the import machinery can reach. The verifier
# covers the superset of what BaseCheckRegistry._file_can_be_imported
# filters, because the loader's own ``sys.path.insert`` makes every
# importable file in the tree reachable, not just the top-level
# non-dunder ``.py`` files the loader's for-loop enumerates.
LOADABLE_SUFFIXES = (".py", ".pyc", ".pyi", ".so", ".pyd")


def _is_loadable(name: str) -> bool:
    return name.endswith(LOADABLE_SUFFIXES)


def _resolves_inside(path: str, root_real: str) -> bool:
    """Whether ``path``'s real (symlink-resolved) location lives under ``root_real``."""
    try:
        target_real = os.path.realpath(path)
    except OSError:
        return False
    target_real = os.path.normpath(target_real)
    # Use ``os.path.commonpath`` to avoid string-prefix bugs (``/a/b`` vs ``/a/bb``).
    try:
        return os.path.commonpath([target_real, root_real]) == root_real
    except ValueError:
        return False


def _walk_loadable_files(root: str) -> "list[str]":
    """Yield every Python-loadable file under ``root`` whose real path stays inside.

    Raises :class:`SignatureVerificationError` if any loadable file's
    real path resolves outside ``root`` (path-escape rejection).
    """
    root_real = os.path.normpath(os.path.realpath(root))
    found: "list[str]" = []
    # ``followlinks=False`` is the default — do not change it. A symlinked
    # subdir is treated as a file entry by the walk and never recursed into.
    for dirpath, _dirnames, filenames in os.walk(root, followlinks=False):
        for name in filenames:
            if name.endswith(SIG_SUFFIX):
                continue
            if not _is_loadable(name):
                continue
            full = os.path.join(dirpath, name)
            if not _resolves_inside(full, root_real):
                raise SignatureVerificationError(
                    f"signature verification failed: {full} resolves outside the verified directory"
                )
            found.append(full)
    return found


def verify_external_checks_dirs(
    dirs: "Iterable[str]",
    keys: "list[VerificationKey]",
) -> "dict[str, bytes]":
    """Verify every Python-loadable file in every dir and return the source map.

    Behaviour contract:

    * If ``keys`` is empty: returns an empty dict and does not walk any
      directory. This is the no-key, no-op path that backwards-compat
      callers rely on.
    * If any file fails verification (missing sig, bad sig, unknown key,
      or path-escape): raises :class:`SignatureVerificationError` listing
      every failure. The exception message names offending relative paths
      so the customer can find them.
    * On success: returns ``{absolute_path: source_bytes}`` covering every
      Python-loadable file in the dir tree. The loader is expected to
      ``exec`` from these bytes and refuse any path not present.
    """
    if not keys:
        return {}

    verified_sources: "dict[str, bytes]" = {}
    failures: "list[str]" = []

    for directory in dirs:
        if not directory or not os.path.isdir(directory):
            continue
        try:
            loadable = _walk_loadable_files(directory)
        except SignatureVerificationError as exc:
            failures.append(str(exc))
            continue

        for payload_path in loadable:
            sig_path = sidecar_path_for(payload_path)
            verification = verify_file_with_bytes(payload_path, sig_path, keys)
            rel = os.path.relpath(payload_path, start=directory)
            if verification.result == VerificationResult.OK:
                verified_sources[payload_path] = verification.payload_bytes
            elif verification.result == VerificationResult.NO_SIGNATURE:
                failures.append(f"missing signature: {rel}")
            else:
                failures.append(f"signature verification failed: {rel}")

    if failures:
        raise SignatureVerificationError(
            "external-checks verification failed:\n  - "
            + "\n  - ".join(failures)
        )

    return verified_sources


__all__ = ["LOADABLE_SUFFIXES", "verify_external_checks_dirs"]
