"""Directory-tree enforcement of signature verification.

This is the module the CLI chokepoint calls. It walks every configured
external-checks directory, identifies every Python-loadable file the
import machinery could reach inside that tree, and requires each one
to be signed by one of the configured keys.

Only ``.py`` files can be trailer-signed (ELF / PE32+ / bytecode
containers have no Python-comment concept). Compiled / binary loadable
file types — ``.pyc``, ``.so``, ``.pyd``, ``.pyi`` — therefore CANNOT
be covered by this verifier. Silently skipping them would let an
attacker drop a ``.so`` next to a verified ``.py`` and have it loaded
transitively, so we reject the whole directory if any such file is
present, listing every offender.

The dict this function returns is the allowlist the loader consumes.
The verifier and the loader must share this enumeration.
"""
from __future__ import annotations

import logging
import os
from typing import Iterable

from .keys import SignatureVerificationError, VerificationKey
from .verifier import VerificationResult, verify_file


logger = logging.getLogger(__name__)


# Python-loadable file extensions the trailer wire format can sign.
LOADABLE_SUFFIXES = (".py",)

# Python-loadable file types that cannot be trailer-signed. Their
# presence in a verified directory is a hard failure (see module
# docstring) — otherwise they would be loaded transitively without
# verification.
_BINARY_LOADABLE_SUFFIXES = (".pyc", ".pyi", ".so", ".pyd")


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
    # ``os.path.commonpath`` avoids the ``/a/b`` vs ``/a/bb`` prefix bug.
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
    mask other failures in the same dir.
    """
    root_real = os.path.normpath(os.path.realpath(root))
    inside: "list[str]" = []
    escape_messages: "list[str]" = []
    binary_messages: "list[str]" = []
    # ``followlinks=False`` is the default — do not change it. A symlinked
    # subdir is treated as a file entry and never recursed into.
    for dirpath, _dirnames, filenames in os.walk(root, followlinks=False):
        for name in filenames:
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

    Overlap = realpath of one entry is the same as or a subpath of
    another's realpath. We refuse overlap because the verified map is
    keyed by absolute payload path and overlap would silently double-load
    files in the loader.

    Errors are accumulated (not raised) so that a config typo and a
    duplicate dir in the same call both surface in one CI cycle.
    Non-existent directories pass through here; the caller validates
    them and emits its own ``does not exist`` failure line.
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

    * Empty ``keys`` → returns ``{}`` and does not walk anything (no-key
      no-op for callers that haven't opted into verification).
    * Any non-empty dir entry that does not resolve to a real directory
      is reported in the failure list. Empty strings are silently
      ignored (CLI default-joining artefact).
    * Duplicate or overlapping (nested) dirs are reported in the same
      failure list; other dirs continue processing so the customer sees
      every problem in one CI cycle.
    * Any per-file failure (missing trailer, bad sig, unknown key,
      path-escape, binary loadable file present) → raises
      :class:`SignatureVerificationError` after every dir has been
      walked, listing every offender by relative path.
    * On success → ``{absolute_path: signed_bytes}`` covering every
      ``.py`` file in the dir tree. The bytes are trailer-stripped; the
      loader should ``exec`` from these and refuse any path not in the
      map.
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
            else:
                failures.append(f"signature verification failed: {rel}")

    if failures:
        raise SignatureVerificationError(
            "external-checks verification failed:\n  - "
            + "\n  - ".join(failures)
        )

    logger.info(
        "external-checks signature verification ok: %d files verified across %d directories",
        len(verified_sources),
        len(unique_dirs),
    )
    return verified_sources


__all__ = ["LOADABLE_SUFFIXES", "verify_external_checks_dirs"]
