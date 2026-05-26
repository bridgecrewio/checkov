"""External-checks signature verification.

Public surface (re-exported below). All other modules in this package are
implementation detail and may change without notice.
"""
from __future__ import annotations

from .enforce import LOADABLE_SUFFIXES, verify_external_checks_dirs
from .keys import SignatureVerificationError, VerificationKey, load_public_keys
from .trailer_format import TRAILER_PREFIX
from .verifier import VerificationResult, verify_bytes, verify_file


__all__ = [
    "LOADABLE_SUFFIXES",
    "SignatureVerificationError",
    "TRAILER_PREFIX",
    "VerificationKey",
    "VerificationResult",
    "load_public_keys",
    "verify_bytes",
    "verify_external_checks_dirs",
    "verify_file",
]
