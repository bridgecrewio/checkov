"""Single-file signature verification.

Cryptographic invariants:

* Strict DER signature decoding via ``decode_dss_signature``.
* Curve and key-type pinning happen at key-load time in :mod:`.keys`.
* ``r`` and ``s`` are checked against the standard ECDSA validity range
  ``[1, n-1]``. ``s`` is NOT further constrained to ``[1, n/2]``
  (low-S) because ``openssl dgst -sha256 -sign`` and AWS KMS produce
  high-S signatures roughly half the time; requiring low-S would
  reject ~50% of customer-produced signatures. This is safe because
  no cache, log or persistent index in this package is keyed by
  signature bytes. If you add such a structure, low-S enforcement
  must come back (or key the structure by
  ``sha256(payload) + key_fingerprint`` instead).
"""
from __future__ import annotations

import enum
import logging
from typing import Iterable

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature

from .keys import VerificationKey
from .trailer_format import (
    decode_hex_signature,
    has_double_trailer,
    has_trailer_prefix,
    parse_trailer,
)


logger = logging.getLogger(__name__)


# secp256r1 group order (SEC 2 §2.4.2 / RFC 5480 §2.1.1.1).
_SECP256R1_N = int(
    "ffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551",
    16,
)


class VerificationResult(enum.Enum):
    """Outcome of verifying a single file."""

    OK = "ok"
    NO_SIGNATURE = "no_signature"
    BAD_SIGNATURE = "bad_signature"
    UNKNOWN_KEY = "unknown_key"
    IO_ERROR = "io_error"
    DOUBLE_TRAILER = "double_trailer"


def _signature_is_well_formed(sig_der: bytes) -> bool:
    """Strict-DER decode plus the standard ECDSA ``[1, n-1]`` range check."""
    try:
        r, s = decode_dss_signature(sig_der)
    except (ValueError, TypeError):
        return False
    if r <= 0 or r >= _SECP256R1_N:
        return False
    if s <= 0 or s >= _SECP256R1_N:
        return False
    return True


def _verify_against_keys(
    payload: bytes,
    sig_der: bytes,
    keys: "Iterable[VerificationKey]",
) -> VerificationResult:
    for key in keys:
        try:
            key.public_key.verify(sig_der, payload, ec.ECDSA(hashes.SHA256()))
            return VerificationResult.OK
        except InvalidSignature:
            continue
    return VerificationResult.UNKNOWN_KEY


def verify_bytes(
    file_bytes: bytes,
    keys: "Iterable[VerificationKey]",
) -> "tuple[VerificationResult, bytes]":
    """Verify already-in-memory trailer-signed bytes.

    Returns ``(result, signed_bytes)`` — ``signed_bytes`` is ``b""`` on
    any non-OK result, and also ``b""`` on the legal one-line
    trailer-only file shape (a signed empty ``__init__.py``).

    Raises :class:`ValueError` if ``keys`` is empty.
    """
    keys_list = list(keys)
    if not keys_list:
        raise ValueError("verify_bytes requires at least one key")

    if has_double_trailer(file_bytes):
        return VerificationResult.DOUBLE_TRAILER, b""

    parsed = parse_trailer(file_bytes)
    if parsed is None:
        # Split "no trailer at all" from "trailer present but malformed"
        # so customer error messages can be useful.
        if has_trailer_prefix(file_bytes):
            return VerificationResult.BAD_SIGNATURE, b""
        return VerificationResult.NO_SIGNATURE, b""

    signed_bytes, hex_payload = parsed
    sig_der = decode_hex_signature(hex_payload)
    if sig_der is None or not _signature_is_well_formed(sig_der):
        return VerificationResult.BAD_SIGNATURE, b""

    result = _verify_against_keys(signed_bytes, sig_der, keys_list)
    if result == VerificationResult.OK:
        return result, signed_bytes
    return result, b""


def verify_file(
    path: str,
    keys: "Iterable[VerificationKey]",
) -> "tuple[VerificationResult, bytes]":
    """Read ``path`` from disk and verify its trailer signature."""
    try:
        with open(path, "rb") as f:
            file_bytes = f.read()
    except OSError as exc:
        logger.debug("cannot read file %s: %s", path, exc)
        return VerificationResult.IO_ERROR, b""
    return verify_bytes(file_bytes, keys)


__all__ = [
    "VerificationResult",
    "verify_bytes",
    "verify_file",
]
