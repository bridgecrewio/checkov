"""Trailer wire format: ``# checkov-digest: <hex-DER-ECDSA-P256-SHA256>\\n``.

Signed bytes = file bytes with the final trailer line + its ``\\n``
stripped (no CRLF normalisation, no BOM stripping).

ECDSA signatures are malleable in ``s`` — do NOT key any cache by
trailer bytes; key by ``sha256(payload) + key_fingerprint`` instead.
"""
from __future__ import annotations

import string


TRAILER_PREFIX = b"# checkov-digest: "

# P-256 ECDSA-DER signatures vary in length between 63 and 72 bytes,
# yielding 126-144 hex chars on the wire. Derivation:
#   * Outer SEQUENCE: 2 bytes (tag + length)
#   * Two INTEGER fields ``r`` and ``s``, each 1-33 bytes of content
#     (32-byte scalar plus an optional leading 0x00 sign-byte when the
#     high bit is set; SEC 1 §C.5 / RFC 5480 §2.1) with 2 bytes of
#     INTEGER tag+length each.
# Producers that emit outside this range (non-conforming signers) are
# rejected at the length-guard before any DER decode.
_HEX_MIN = 126
_HEX_MAX = 144

_LOWERCASE_HEX_BYTES = frozenset((string.digits + "abcdef").encode("ascii"))


def parse_trailer(file_bytes: bytes) -> "tuple[bytes, bytes] | None":
    """Return ``(signed_bytes, hex_payload)`` or ``None`` on any structural failure."""
    if not file_bytes or not file_bytes.endswith(b"\n"):
        return None

    body = file_bytes[:-1]
    last_nl = body.rfind(b"\n")
    trailer_line = body[last_nl + 1:]

    if not trailer_line.startswith(TRAILER_PREFIX):
        return None

    hex_payload = trailer_line[len(TRAILER_PREFIX):]
    if not (_HEX_MIN <= len(hex_payload) <= _HEX_MAX):
        return None
    if not all(b in _LOWERCASE_HEX_BYTES for b in hex_payload):
        return None

    signed_bytes = file_bytes[:last_nl + 1] if last_nl >= 0 else b""
    return signed_bytes, hex_payload


def has_trailer_prefix(file_bytes: bytes) -> bool:
    if not file_bytes or not file_bytes.endswith(b"\n"):
        return False
    body = file_bytes[:-1]
    last_nl = body.rfind(b"\n")
    return body[last_nl + 1:].startswith(TRAILER_PREFIX)


def has_double_trailer(file_bytes: bytes) -> bool:
    """True iff the last TWO lines both start with the trailer prefix
    (i.e. the signing recipe was run twice without resetting the file).
    """
    if not file_bytes or not file_bytes.endswith(b"\n"):
        return False
    body = file_bytes[:-1]
    last_nl = body.rfind(b"\n")
    if last_nl < 0:
        return False
    if not body[last_nl + 1:].startswith(TRAILER_PREFIX):
        return False
    body_without_last = body[:last_nl]
    prev_nl = body_without_last.rfind(b"\n")
    return body_without_last[prev_nl + 1:].startswith(TRAILER_PREFIX)


def decode_hex_signature(hex_payload: bytes) -> "bytes | None":
    try:
        return bytes.fromhex(hex_payload.decode("ascii"))
    except (UnicodeDecodeError, ValueError):
        return None


__all__ = [
    "TRAILER_PREFIX",
    "decode_hex_signature",
    "has_double_trailer",
    "has_trailer_prefix",
    "parse_trailer",
]
