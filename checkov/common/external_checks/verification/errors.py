"""Crypto-free error types for external-check verification.

This module is intentionally crypto-free so it can be imported from
``main.py`` and ``base_check_registry.py`` without pulling in
``cryptography`` (which is not a core checkov dependency — see the
package ``__init__.py`` for the full rationale).
"""
from __future__ import annotations


class SignatureVerificationError(Exception):
    """Raised when verification fails for any reason."""


__all__ = ["SignatureVerificationError"]
