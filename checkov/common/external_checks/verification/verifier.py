"""Single-file signature verification under the in-file trailer wire format.

Each verified ``.py`` file carries its signature as a final-line comment
of the form ``# checkov-digest: <hex>\\n``. The verifier reads the file
once, parses out the trailer, and verifies against the trailer-stripped
bytes — those same trailer-stripped bytes are what the loader will
execute, so the bytes that were hashed are the bytes that get run.

Cryptographic invariants:

* Strict DER signature decoding via ``decode_dss_signature``. Anything
  not canonically DER-encoded is rejected before any elliptic-curve
  operation.
* Curve and key-type pinning happen at key-load time in :mod:`.keys`;
  this module trusts the caller-supplied list.
* ``r`` and ``s`` are checked against the standard ECDSA validity range
  ``[1, n-1]``. ``s`` is **not** further constrained to ``[1, n/2]``
  (low-S).

  Rationale for accepting both S halves: ECDSA signatures are equivalent
  in pairs — ``(r, s)`` and ``(r, n-s)`` both verify the same message
  under the same key. ``openssl dgst -sha256 -sign`` and AWS KMS produce
  ``s > n/2`` roughly half the time; requiring low-S would reject ~50%
  of customer-produced signatures. This is safe because no cache, log,
  dedup table, or persistent index in this package is keyed by signature
  bytes or any hash thereof.

  Maintenance note: if you ever add such a structure (cache keyed by
  ``sha256(sig)`` is the textbook example), low-S enforcement must come
  back. The safer pattern is to key by ``sha256(payload) +
  key_fingerprint`` instead.
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
from .trailer_format import decode_hex_signature, has_trailer_prefix, parse_trailer


logger = logging.getLogger(__name__)


# secp256r1 group order; see SEC 2 §2.4.2 or RFC 5480 §2.1.1.1.
_SECP256R1_N = int(
    "ffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551",
    16,
)


class VerificationResult(enum.Enum):
    """Outcome of verifying a single file."""

    OK = "ok"
    NO_SIGNATURE = "no_signature"     # no trailer line present (or file unreadable)
    BAD_SIGNATURE = "bad_signature"   # trailer present but cryptographically invalid
    UNKNOWN_KEY = "unknown_key"       # well-formed signature, but no configured key verifies
    IO_ERROR = "io_error"             # file present but unreadable (perms, ENAMETOOLONG, ...)


def _signature_is_well_formed(sig_der: bytes) -> bool:
    """Strict-DER decode plus the standard ECDSA validity range check."""
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
    """Verify a trailer-signed file's bytes already in memory.

    Returns ``(result, signed_bytes)``. ``signed_bytes`` is the trailer-
    stripped payload the loader should execute; it is ``b""`` on any
    non-``OK`` result. (It is also ``b""`` on the legal one-line
    trailer-only file shape — a signed empty ``__init__.py`` — in which
    case the result is ``OK``.)

    Raises :class:`ValueError` if ``keys`` is empty.
    """
    keys_list = list(keys)
    if not keys_list:
        raise ValueError("verify_bytes requires at least one key")

    parsed = parse_trailer(file_bytes)
    if parsed is None:
        # Distinguish "no trailer at all" (NO_SIGNATURE — you forgot to
        # sign this) from "trailer present but malformed" (BAD_SIGNATURE
        # — you signed it wrong), so customer error messages are useful.
        if has_trailer_prefix(file_bytes):
            return VerificationResult.BAD_SIGNATURE, b""
        return VerificationResult.NO_SIGNATURE, b""

    signed_bytes, hex_payload = parsed
    sig_der = decode_hex_signature(hex_payload)
    if sig_der is None:
        # Should be unreachable — parse_trailer's alphabet/length guards
        # catch this — but fail closed if it ever leaks through.
        return VerificationResult.BAD_SIGNATURE, b""
    if not _signature_is_well_formed(sig_der):
        return VerificationResult.BAD_SIGNATURE, b""

    result = _verify_against_keys(signed_bytes, sig_der, keys_list)
    if result == VerificationResult.OK:
        return result, signed_bytes
    return result, b""


def verify_file(
    path: str,
    keys: "Iterable[VerificationKey]",
) -> "tuple[VerificationResult, bytes]":
    """Read ``path`` from disk and verify its trailer signature.

    Returns ``(result, signed_bytes)`` per :func:`verify_bytes`. Returns
    ``(IO_ERROR, b"")`` if the file exists but cannot be read.
    """
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
