"""Process-global allowlist of verified external-check sources.

Bridges the chokepoint (``main.py:get_external_checks_dir``) and the
loader (``BaseCheckRegistry.load_external_checks``) without threading a
``verified_sources`` kwarg through every per-language runner's
``load_external_checks(directory)`` call site.

Lifecycle:

1. The chokepoint calls :func:`verify_and_register` once before any
   scan runs. On success the in-memory ``{absolute_path: signed_bytes}``
   map is stored here and :func:`is_verification_active` returns True
   for the rest of the process.
2. Each runner's ``load_external_checks`` calls
   :func:`get_verified_sources_for_directory` to retrieve the slice of
   the map under its directory.

Tests must call :func:`reset_for_tests` in teardown.
"""
from __future__ import annotations

import logging
import os
from typing import Dict, Iterable, List, Optional


logger = logging.getLogger(__name__)


# ``None`` = verification not active for this process.
# Empty dict = verification active but no .py files were found.
_verified_sources: Optional[Dict[str, bytes]] = None


def is_verification_active() -> bool:
    """True iff :func:`verify_and_register` has been called this process."""
    return _verified_sources is not None


def verify_and_register(
    dirs: Iterable[str],
    public_key_paths: List[str],
) -> None:
    """Verify every ``.py`` file in ``dirs`` and stash the source map.

    No-op when ``public_key_paths`` is empty (backward compatibility).
    Raises :class:`SignatureVerificationError` on any verification failure.
    """
    global _verified_sources

    if not public_key_paths:
        return

    # Lazy imports: ``enforce`` and ``keys`` transitively import the
    # ``cryptography`` package, which is NOT a core checkov dependency.
    # Hoisting these imports would crash the legacy code path on every
    # install without ``cryptography``.
    from .enforce import verify_external_checks_dirs
    from .keys import load_public_keys

    keys = load_public_keys(public_key_paths)
    verified = verify_external_checks_dirs(dirs, keys)
    # Realpath-normalise keys so the loader's canonical-path lookup
    # works even when ``--external-checks-dir`` is itself a symlink.
    _verified_sources = {
        os.path.normpath(os.path.realpath(p)): b for p, b in verified.items()
    }
    logger.info("external-checks verification registered: %d files", len(_verified_sources))


def get_verified_sources_for_directory(directory: str) -> "Optional[Dict[str, bytes]]":
    """Return the subset of the global map under ``directory``.

    Returns ``None`` if verification is not active (legacy disk-load
    runs unchanged). Returns an empty dict if verification is active
    but no verified files belong to this directory — the loader then
    refuses every on-disk ``.py``, which is the documented refusal
    behaviour for an empty allowlist.
    """
    if _verified_sources is None:
        return None
    directory_real = os.path.normpath(os.path.realpath(directory))
    prefix = directory_real + os.sep
    return {
        path: source_bytes
        for path, source_bytes in _verified_sources.items()
        if path == directory_real or path.startswith(prefix)
    }


def reset_for_tests() -> None:
    """Clear the global allowlist. Tests must call this in teardown."""
    global _verified_sources
    _verified_sources = None


__all__ = [
    "get_verified_sources_for_directory",
    "is_verification_active",
    "reset_for_tests",
    "verify_and_register",
]
