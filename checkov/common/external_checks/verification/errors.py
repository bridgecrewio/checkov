"""Error types for external-checks signature verification."""
from __future__ import annotations


class SignatureVerificationError(Exception):
    pass


__all__ = ["SignatureVerificationError"]
