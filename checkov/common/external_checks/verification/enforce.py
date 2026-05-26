"""Directory-tree enforcement of signature verification.

Only ``.py`` files can be trailer-signed (ELF / PE / bytecode containers
have no Python-comment concept). Binary loadable types (``.pyc``,
``.so``, ``.pyd``, ``.pyi``) anywhere except inside ``__pycache__/``
are a hard failure — silently skipping them would let the import
machinery load an unverified compiled module that happens to share a
stem with a signed ``.py``.

``__pycache__/`` subdirectories are silently skipped (see
:data:`_SKIPPED_DIRECTORY_NAMES`).
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

# Skipped during the walk. ``__pycache__`` is a CPython artefact that
# can contain ``.pyc`` files from previous (verified or unverified) runs;
# treating its contents as binary loadable failures would produce false
# positives. The loader's meta-path finder intercepts allowlisted names
# BEFORE the default ``PathFinder`` ever consults ``__pycache__``, so
# skipping the directory cannot be used to bypass verification.
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
    """Walk ``root`` and partition files into three buckets.

    Returns ``(inside_paths, escape_messages, binary_rejection_messages)``.
    Never raises so a single bad symlink or stray binary file does not
    mask other failures.
    """
    root_real = os.path.normpath(os.path.realpath(root))
    inside: "list[str]" = []
    escape_messages: "list[str]" = []
    binary_messages: "list[str]" = []
    # ``followlinks=False`` is the default — do not change it.
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        # In-place pruning is how ``os.walk`` stops recursing.
        dirnames[:] = [d for d in dirnames if d not in _SKIPPED_DIRECTORY_NAMES]
        for name in filenames:
            # Skip files the loader would never execute — dotfiles
            # (``.signed_backup.py``, ``.swp``-style editor backups,
            # ``.foo.py``) are excluded by
            # ``BaseCheckRegistry._file_can_be_imported`` on the legacy
            # path; aligning the verifier with the loader avoids
            # false-positive rejections for files the import machinery
            # would never reach.
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

    Overlap (one entry's realpath is the same as or a subpath of
    another's) is refused because the verified map is keyed by absolute
    payload path and overlap would silently double-load files.
    Errors are accumulated, not raised, so a config typo and a duplicate
    dir in the same call both surface in one CI cycle.
    """
    unique_dirs: "list[str]" = []
    overlap_errors: "list[str]" = []
    seen: "dict[str, str]" = {}  # realpath -> original directory string
    for directory in dirs:
        if not directory:
            continue
        if not os.path.isdir(directory):
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
    """Verify every Python-loadable file in every dir and return the source map.

    * Empty ``keys`` → returns ``{}`` and does not walk anything.
    * Failures (missing trailer, bad sig, unknown key, path-escape,
      binary loadable file, duplicate/overlapping/missing dir) →
      :class:`SignatureVerificationError` after every dir has been
      walked, listing every offender by relative path.
    * On success → ``{absolute_path: signed_bytes}``. Bytes are
      trailer-stripped; the loader execs from these.
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
