"""Process-global verified-sources registry: chokepoint ↔ loader bridge."""
from __future__ import annotations

import logging
import os
from typing import Dict, Iterable, List, Optional

from .enforce import verify_external_checks_dirs
from .keys import load_public_keys


logger = logging.getLogger(__name__)


# None = inactive; empty dict = active but no .py files found.
_verified_sources: Optional[Dict[str, bytes]] = None


def is_verification_active() -> bool:
    return _verified_sources is not None


def verify_and_register(
    dirs: Iterable[str],
    public_key_paths: List[str],
) -> None:
    """No-op when ``public_key_paths`` is empty. Raises on verification failure.

    On failure the registry is cleared (set back to inactive).
    """
    global _verified_sources

    if not public_key_paths:
        return

    keys = load_public_keys(public_key_paths)
    try:
        verified = verify_external_checks_dirs(dirs, keys)
    except BaseException:
        _verified_sources = None
        raise
    _verified_sources = {
        os.path.normpath(os.path.realpath(p)): b for p, b in verified.items()
    }
    logger.info("external-checks verification registered: %d files", len(_verified_sources))


def get_verified_sources_for_directory(directory: str) -> "Optional[Dict[str, bytes]]":
    """Return None when inactive; else the subset under ``directory``."""
    if _verified_sources is None:
        return None
    directory_real = os.path.normpath(os.path.realpath(directory))
    prefix = directory_real + os.sep
    return {
        path: source_bytes
        for path, source_bytes in _verified_sources.items()
        if path == directory_real or path.startswith(prefix)
    }


def get_all_verified_sources() -> "Optional[Dict[str, bytes]]":
    """Return the FULL registry snapshot, or ``None`` when inactive.

    Used by the loader to serve cross-directory transitive imports
    from verified bytes (otherwise a verified check in dir-A that does
    ``import shared_helper`` from dir-B would fall through to the
    unverified on-disk file).
    """
    if _verified_sources is None:
        return None
    return dict(_verified_sources)


def reset_for_tests() -> None:
    global _verified_sources
    _verified_sources = None


__all__ = [
    "get_all_verified_sources",
    "get_verified_sources_for_directory",
    "is_verification_active",
    "reset_for_tests",
    "verify_and_register",
]
