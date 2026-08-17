"""Trailer wire format: ``# checkov-digest: <hex-DER-ECDSA-P256-SHA256>\\n``."""
from __future__ import annotations

import string


TRAILER_PREFIX = b"# checkov-digest: "

# P-256 DER signatures are 63-72 bytes (SEC 1 §C.5 / RFC 5480 §2.1) → 126-144 hex chars.
_HEX_MIN = 126
_HEX_MAX = 144

_LOWERCASE_HEX_BYTES = frozenset((string.digits + "abcdef").encode("ascii"))


def _split_last_line(file_bytes: bytes) -> "tuple[bytes, int, bytes] | None":
    if not file_bytes or not file_bytes.endswith(b"\n"):
        return None
    body = file_bytes[:-1]
    last_nl = body.rfind(b"\n")
    return body, last_nl, body[last_nl + 1:]


def parse_trailer(file_bytes: bytes) -> "tuple[bytes, bytes] | None":
    split = _split_last_line(file_bytes)
    if split is None:
        return None
    _body, last_nl, trailer_line = split

    if not trailer_line.startswith(TRAILER_PREFIX):
        return None

    hex_payload = trailer_line[len(TRAILER_PREFIX):]
    if not (_HEX_MIN <= len(hex_payload) <= _HEX_MAX):
        return None
    if not all(b in _LOWERCASE_HEX_BYTES for b in hex_payload):
        return None

    # last_nl == -1 → file is the trailer line only → empty signed body.
    signed_bytes = file_bytes[:last_nl + 1] if last_nl >= 0 else b""
    return signed_bytes, hex_payload


def has_trailer_prefix(file_bytes: bytes) -> bool:
    split = _split_last_line(file_bytes)
    if split is None:
        return False
    return split[2].startswith(TRAILER_PREFIX)


def has_double_trailer(file_bytes: bytes) -> bool:
    """True iff the last TWO lines both start with the trailer prefix."""
    split = _split_last_line(file_bytes)
    if split is None:
        return False
    body, last_nl, last_line = split
    if last_nl < 0:
        return False
    if not last_line.startswith(TRAILER_PREFIX):
        return False
    body_without_last = body[:last_nl]
    prev_nl = body_without_last.rfind(b"\n")
    return body_without_last[prev_nl + 1:].startswith(TRAILER_PREFIX)


def decode_hex_signature(hex_payload: bytes) -> "bytes | None":
    try:
        return bytes.fromhex(hex_payload.decode("ascii"))
    except ValueError:
        # UnicodeDecodeError is a subclass of ValueError, so this catches both
        # non-ASCII payloads and non-hex characters in one branch.
        return None


__all__ = [
    "TRAILER_PREFIX",
    "decode_hex_signature",
    "has_double_trailer",
    "has_trailer_prefix",
    "parse_trailer",
]
