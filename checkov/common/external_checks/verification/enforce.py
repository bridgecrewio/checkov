"""Directory-tree enforcement of signature verification.

Binary loadable files (``.pyc``, ``.so``, ``.pyd``, ``.pyi``) outside
``__pycache__/`` are a hard failure — silently skipping them would let
the import machinery load an unverified compiled module sharing a stem
with a signed ``.py``.
"""
from __future__ import annotations

import logging
import os
from typing import Iterable

from .errors import SignatureVerificationError
from .keys import VerificationKey
from .verifier import VerificationResult, verify_file


logger = logging.getLogger(__name__)


LOADABLE_SUFFIXES = (".py",)

_BINARY_LOADABLE_SUFFIXES = (".pyc", ".pyi", ".so", ".pyd")

# ``__pycache__`` is skipped (not failed): it may hold .pyc artefacts
# from prior runs. The meta-path finder intercepts allowlisted names
# before ``PathFinder`` consults ``__pycache__``, so this is not a bypass.
_SKIPPED_DIRECTORY_NAMES = frozenset({"__pycache__"})


def _is_loadable(name: str) -> bool:
    return name.endswith(LOADABLE_SUFFIXES)


def _is_binary_loadable(name: str) -> bool:
    return name.endswith(_BINARY_LOADABLE_SUFFIXES)


def _resolves_inside(path: str, root_real: str) -> "tuple[bool, str]":
    """Return ``(inside, reason)``. ``reason`` is empty on success."""
    try:
        target_real = os.path.realpath(path)
    except OSError as exc:
        return False, f"realpath failed: {exc}"
    target_real = os.path.normpath(target_real)
    if not os.path.exists(target_real):
        return False, "symlink target does not exist"
    try:
        if os.path.commonpath([target_real, root_real]) != root_real:
            return False, "resolves outside the verified directory"
    except ValueError as exc:
        return False, f"path comparison failed: {exc}"
    return True, ""


def _walk_loadable_files(
    root: str,
) -> "tuple[list[str], list[str], list[str]]":
    """Walk ``root`` → ``(inside_paths, escape_messages, binary_rejections)``.

    Never raises so a single bad symlink or stray binary does not mask
    other failures.
    """
    root_real = os.path.normpath(os.path.realpath(root))
    inside: "list[str]" = []
    escape_messages: "list[str]" = []
    binary_messages: "list[str]" = []
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        # In-place mutation is how os.walk stops recursing into dirnames.
        dirnames[:] = [d for d in dirnames if d not in _SKIPPED_DIRECTORY_NAMES]
        for name in filenames:
            # Align with BaseCheckRegistry._file_can_be_imported, which
            # skips dotfiles — the verifier must not reject files the
            # loader would never reach.
            if name.startswith("."):
                continue
            if _is_binary_loadable(name):
                full = os.path.join(dirpath, name)
                binary_messages.append(
                    "binary file not supported under trailer signing "
                    f"(only .py is covered): {os.path.relpath(full, start=root)}"
                )
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
    return inside, escape_messages, binary_messages


def _normalise_and_dedupe(
    dirs: "Iterable[str]",
) -> "tuple[list[str], list[str]]":
    """Return ``(unique_dirs, overlap_errors)``.

    Overlap is refused because the verified map is keyed by absolute
    payload path; overlapping dirs would silently double-load files.
    """
    unique_dirs: "list[str]" = []
    overlap_errors: "list[str]" = []
    seen: "dict[str, str]" = {}  # realpath -> original directory string
    for directory in dirs:
        if not directory:
            continue
        if not os.path.isdir(directory):
            # Non-existent / non-dir paths skip realpath + overlap
            # normalisation: they cannot be resolved, and the missing-dir
            # diagnostic in the main loop will surface them by name. As a
            # consequence, two `dirs` arguments that are both typos for
            # the same path each produce their own "does not exist" line
            # (harmless, but explains the asymmetry with the dir-vs-dir
            # duplicate case below).
            unique_dirs.append(directory)
            continue
        rp = os.path.normpath(os.path.realpath(directory))
        if rp in seen:
            overlap_errors.append(f"duplicate external-checks directory: {directory}")
            continue
        overlap = None
        for other_rp in seen:
            if rp.startswith(other_rp + os.sep) or other_rp.startswith(rp + os.sep):
                overlap = seen[other_rp]
                break
        if overlap is not None:
            overlap_errors.append(
                f"overlapping external-checks directories: {directory} and {overlap}"
            )
            continue
        seen[rp] = directory
        unique_dirs.append(directory)
    return unique_dirs, overlap_errors


def verify_external_checks_dirs(
    dirs: "Iterable[str]",
    keys: "list[VerificationKey]",
) -> "dict[str, bytes]":
    """Verify every ``.py`` under every dir; raise on any failure.

    Empty ``keys`` → ``{}`` (no walk). All failures across all dirs are
    accumulated before raising, so one CI cycle surfaces everything.
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

        loadable, escape_messages, binary_messages = _walk_loadable_files(directory)
        failures.extend(escape_messages)
        failures.extend(binary_messages)

        for payload_path in loadable:
            result, signed_bytes = verify_file(payload_path, keys)
            rel = os.path.relpath(payload_path, start=directory)
            if result == VerificationResult.OK:
                verified_sources[payload_path] = signed_bytes
            elif result == VerificationResult.NO_SIGNATURE:
                failures.append(f"missing signature: {rel}")
            elif result == VerificationResult.IO_ERROR:
                failures.append(f"payload file is unreadable: {rel}")
            elif result == VerificationResult.DOUBLE_TRAILER:
                failures.append(
                    f"file appears to be signed twice (two trailer lines at end of file): {rel}"
                )
            else:
                failures.append(f"signature verification failed: {rel}")

    if failures:
        raise SignatureVerificationError("\n".join(f"  - {f}" for f in failures))

    logger.info(
        "external-checks signature verification ok: %d files verified across %d directories",
        len(verified_sources),
        len(unique_dirs),
    )
    return verified_sources


__all__ = ["LOADABLE_SUFFIXES", "verify_external_checks_dirs"]
