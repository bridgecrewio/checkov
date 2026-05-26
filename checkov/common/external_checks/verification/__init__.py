"""External-checks signature verification.

Public surface (re-exported below). All other modules in this package are
implementation detail and may change without notice.
"""
from __future__ import annotations

from .enforce import verify_external_checks_dirs
from .keys import SignatureVerificationError, VerificationKey, load_public_keys
from .verifier import (
    FileVerification,
    VerificationResult,
    verify_bytes,
    verify_file,
    verify_file_with_bytes,
)


__all__ = [
    "FileVerification",
    "SignatureVerificationError",
    "VerificationKey",
    "VerificationResult",
    "load_public_keys",
    "verify_bytes",
    "verify_external_checks_dirs",
    "verify_file",
    "verify_file_with_bytes",
]
