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


def _resolves_inside(path: str, root_real: str) -> "tuple[bool, str]":
    """Return ``(inside, reason)``. ``reason`` is empty on success."""
    try:
        target_real = os.path.realpath(path)
    except OSError as exc:
        return False, f"realpath failed: {exc}"
    target_real = os.path.normpath(target_real)
    if not os.path.exists(target_real):
        return False, "symlink target does not exist"
    # Use ``os.path.commonpath`` to avoid string-prefix bugs (``/a/b`` vs ``/a/bb``).
    try:
        if os.path.commonpath([target_real, root_real]) != root_real:
            return False, "resolves outside the verified directory"
    except ValueError as exc:
        return False, f"path comparison failed: {exc}"
    return True, ""


def _walk_loadable_files(root: str) -> "tuple[list[str], list[str]]":
    """Walk ``root`` and partition loadable files into (inside, escaped).

    Returns ``(inside_paths, escape_messages)``. The caller decides whether
    to raise; this function never raises so a single bad symlink does not
    mask other failures in the same dir.
    """
    root_real = os.path.normpath(os.path.realpath(root))
    inside: "list[str]" = []
    escape_messages: "list[str]" = []
    # ``followlinks=False`` is the default — do not change it. A symlinked
    # subdir is treated as a file entry by the walk and never recursed into.
    for dirpath, _dirnames, filenames in os.walk(root, followlinks=False):
        for name in filenames:
            if name.endswith(SIG_SUFFIX):
                continue
            if not _is_loadable(name):
                continue
            full = os.path.join(dirpath, name)
            ok, reason = _resolves_inside(full, root_real)
            if not ok:
                escape_messages.append(
                    f"path resolves outside the verified directory "
                    f"({reason}): {os.path.relpath(full, start=root)}"
                )
                continue
            inside.append(full)
    return inside, escape_messages


def _normalise_and_dedupe(
    dirs: "Iterable[str]",
) -> "tuple[list[str], list[str]]":
    """Return ``(unique_dirs, overlap_errors)``.

    Overlap = the realpath of one entry is the same as or a subpath of
    another's realpath. We refuse overlap because the verified map is
    keyed by absolute payload path and overlap would silently double-load
    files in the Phase-2 loader.

    Errors are accumulated (not raised) so that a single config typo and
    a duplicate dir in the same call are both reported to the customer.
    Non-existent directories pass through untouched; the caller validates
    them and emits its own ``does not exist`` failure line.
    """
    unique_dirs: "list[str]" = []
    overlap_errors: "list[str]" = []
    seen: "dict[str, str]" = {}  # realpath -> original directory string
    for directory in dirs:
        if not directory:
            continue
        if not os.path.isdir(directory):
            # Caller validates non-existent dirs separately (see F1).
            unique_dirs.append(directory)
            continue
        rp = os.path.normpath(os.path.realpath(directory))
        if rp in seen:
            overlap_errors.append(
                f"duplicate external-checks directory: {directory}"
            )
            continue
        overlap = None
        for other_rp in seen:
            if rp.startswith(other_rp + os.sep) or other_rp.startswith(rp + os.sep):
                overlap = seen[other_rp]
                break
        if overlap is not None:
            overlap_errors.append(
                f"overlapping external-checks directories: "
                f"{directory} and {overlap}"
            )
            continue
        seen[rp] = directory
        unique_dirs.append(directory)
    return unique_dirs, overlap_errors


def verify_external_checks_dirs(
    dirs: "Iterable[str]",
    keys: "list[VerificationKey]",
) -> "dict[str, bytes]":
    """Verify every Python-loadable file in every dir and return the source map.

    Behaviour contract:

    * If ``keys`` is empty: returns an empty dict and does not walk any
      directory. This is the no-key, no-op path that backwards-compat
      callers rely on.
    * If any entry in ``dirs`` is non-empty but does not resolve to a real
      directory: that entry is reported in the failure list and the call
      raises after every dir has been processed. Empty strings are ignored
      (they are an artefact of CLI default-joining).
    * Duplicate or overlapping (nested) dirs are reported in the same
      failure list; processing of other dirs continues so the customer sees
      every problem in a single CI cycle.
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

    unique_dirs, overlap_errors = _normalise_and_dedupe(dirs)

    verified_sources: "dict[str, bytes]" = {}
    failures: "list[str]" = list(overlap_errors)

    for directory in unique_dirs:
        if not os.path.isdir(directory):
            failures.append(
                f"external-checks directory does not exist or is not a directory: {directory}"
            )
            continue

        loadable, escape_messages = _walk_loadable_files(directory)
        failures.extend(escape_messages)

        for payload_path in loadable:
            sig_path = sidecar_path_for(payload_path)
            verification = verify_file_with_bytes(payload_path, sig_path, keys)
            rel = os.path.relpath(payload_path, start=directory)
            if verification.result == VerificationResult.OK:
                verified_sources[payload_path] = verification.payload_bytes
            elif verification.result == VerificationResult.NO_SIGNATURE:
                failures.append(f"missing signature: {rel}")
            elif verification.result == VerificationResult.IO_ERROR:
                failures.append(f"payload file is unreadable: {rel}")
            else:
                failures.append(f"signature verification failed: {rel}")

    if failures:
        raise SignatureVerificationError(
            "external-checks verification failed:\n  - "
            + "\n  - ".join(failures)
        )

    # ``unique_dirs`` has already been filtered (empty strings dropped) and
    # validated (every entry is an existing dir, since failures would have
    # caused the early raise above). No extra syscalls needed.
    logger.info(
        "external-checks signature verification ok: %d files verified across %d directories",
        len(verified_sources),
        len(unique_dirs),
    )
    return verified_sources


__all__ = ["LOADABLE_SUFFIXES", "verify_external_checks_dirs"]
