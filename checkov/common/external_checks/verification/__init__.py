"""External-checks signature verification."""
from __future__ import annotations

from .enforce import verify_external_checks_dirs
from .errors import SignatureVerificationError
from .keys import VerificationKey, load_public_keys
from .trailer_format import TRAILER_PREFIX, has_double_trailer
from .verifier import VerificationResult, verify_bytes, verify_file


__all__ = [
    "SignatureVerificationError",
    "TRAILER_PREFIX",
    "VerificationKey",
    "VerificationResult",
    "has_double_trailer",
    "load_public_keys",
    "verify_bytes",
    "verify_external_checks_dirs",
    "verify_file",
]
