"""Crypto-free error types — safe to import without ``cryptography``."""
from __future__ import annotations


class SignatureVerificationError(Exception):
    pass


__all__ = ["SignatureVerificationError"]
