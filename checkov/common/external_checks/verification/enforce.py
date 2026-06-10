"""Directory-tree enforcement of signature verification."""
from __future__ import annotations

import logging
import os
from typing import Iterable

from .errors import SignatureVerificationError
from .keys import VerificationKey
from .verifier import VerificationResult, verify_file


logger = logging.getLogger(__name__)


LOADABLE_SUFFIXES = (".py",)
_SKIPPED_DIRECTORY_NAMES = frozenset({"__pycache__"})

_FAILURE_MESSAGE_TEMPLATES: "dict[VerificationResult, str]" = {
    VerificationResult.NO_SIGNATURE: "missing signature: {rel}",
    VerificationResult.IO_ERROR: "payload file is unreadable: {rel}",
    VerificationResult.DOUBLE_TRAILER: (
        "file appears to be signed twice (two trailer lines at end of file): {rel}"
    ),
}
_GENERIC_FAILURE_MESSAGE = "signature verification failed: {rel}"


def _is_loadable(name: str) -> bool:
    return name.endswith(LOADABLE_SUFFIXES)


def _resolves_inside(path: str, root_real: str) -> "tuple[bool, str]":
    """Return ``(inside, reason)``; ``reason`` is empty on success."""
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
) -> "tuple[list[str], list[str]]":
    """Walk ``root`` → ``(inside_paths, escape_messages)``.

    Only ``.py`` files are considered for verification. Any other file
    type (including binary loadables such as ``.pyc`` / ``.so``) is
    silently ignored — Checkov never imports them via the external-checks
    loader, so they are not in scope for trailer signing.
    """
    root_real = os.path.normpath(os.path.realpath(root))
    inside: "list[str]" = []
    escape_messages: "list[str]" = []
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        dirnames[:] = [d for d in dirnames if d not in _SKIPPED_DIRECTORY_NAMES]
        for name in filenames:
            if name.startswith("."):
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
    """Return ``(unique_dirs, overlap_errors)``."""
    unique_dirs: "list[str]" = []
    overlap_errors: "list[str]" = []
    seen: "dict[str, str]" = {}
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
    """Verify every ``.py`` under every dir; raise on any failure."""
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
            result, signed_bytes = verify_file(payload_path, keys)
            rel = os.path.relpath(payload_path, start=directory)
            if result == VerificationResult.OK:
                verified_sources[payload_path] = signed_bytes
                continue
            template = _FAILURE_MESSAGE_TEMPLATES.get(result, _GENERIC_FAILURE_MESSAGE)
            failures.append(template.format(rel=rel))

    if failures:
        raise SignatureVerificationError("\n".join(f"  - {f}" for f in failures))

    logger.info(
        "external-checks signature verification ok: %d files verified across %d directories",
        len(verified_sources),
        len(unique_dirs),
    )
    return verified_sources


__all__ = ["verify_external_checks_dirs"]
