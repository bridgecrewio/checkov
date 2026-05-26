"""In-file trailer wire format for external-check signatures.

Each signed ``.py`` file ends with exactly one line of the form::

    # checkov-digest: <lowercase-hex-DER-ECDSA-P256-SHA256-signature>\\n

Wire-format rules (each is binding):

* Trailer prefix is exactly ``b"# checkov-digest: "`` — one ASCII space
  after the colon.
* Payload is the DER ECDSA signature in lowercase hex, length in
  ``[126, 144]``.
* Trailer is the final line, terminated by exactly one ``\\n``.
* Signed bytes = file bytes with the trailer line + its ``\\n`` stripped.
  No CRLF normalisation, no BOM stripping.

Do not build any cache keyed by trailer bytes. ECDSA signatures are
malleable in their ``s`` component — ``(r, s)`` and ``(r, n-s)`` both
verify under the same key for the same payload but encode differently.
Key by ``sha256(payload) + key_fingerprint`` instead.
"""
from __future__ import annotations

import string


TRAILER_PREFIX = b"# checkov-digest: "

# P-256 DER ECDSA signatures are 70-72 bytes typically and 63-72 with
# leading-zero stripping → 126-144 hex chars.
_HEX_MIN = 126
_HEX_MAX = 144

_LOWERCASE_HEX_BYTES = frozenset((string.digits + "abcdef").encode("ascii"))


def parse_trailer(file_bytes: bytes) -> "tuple[bytes, bytes] | None":
    """Parse trailer-signed file bytes into ``(signed_bytes, hex_payload)``.

    Returns ``None`` on any structural failure (no terminating ``\\n``,
    wrong prefix, payload length out of range, non-lowercase-hex byte
    in payload). On success, ``signed_bytes`` are the bytes to hash and
    ``hex_payload`` is the ASCII hex to decode as a DER signature.
    """
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
    """True iff the file's last ``\\n``-terminated line starts with the trailer prefix."""
    if not file_bytes or not file_bytes.endswith(b"\n"):
        return False
    body = file_bytes[:-1]
    last_nl = body.rfind(b"\n")
    return body[last_nl + 1:].startswith(TRAILER_PREFIX)


def has_double_trailer(file_bytes: bytes) -> bool:
    """True iff the last AND second-to-last lines both start with the trailer prefix.

    Detects "the signer ran the signing recipe twice without resetting
    the file" — a recipe re-run cannot happen by editor mishap; only by
    deliberate / scripted re-signing.
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
    """Decode a hex payload into raw DER signature bytes. Returns ``None`` on failure."""
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
