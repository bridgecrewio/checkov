"""In-file trailer wire-format parser for external-check signatures.

Each signed ``.py`` file ends with a single trailer line of the exact form::

    # checkov-digest: <lowercase-hex-DER-signature>\\n

Rules (each is binding — changing any of them is a wire-format break):

* Trailer prefix is exactly ``b"# checkov-digest: "`` — one ASCII space
  after the colon, nothing else. No tabs, no padding.
* Payload is the DER-encoded ECDSA signature, lowercase hex, length in
  ``[126, 144]`` (the legitimate P-256 DER range).
* Trailer is the very last line, terminated by exactly one ``\\n``.
* Signed bytes = file bytes with the trailer line + its ``\\n`` stripped.
  No CRLF→LF normalisation, no BOM stripping, no Unicode normalisation.
  The bytes on disk before the trailer was appended are what the signer
  signed and what the verifier hashes.

Do **not** build a cache keyed by trailer bytes or by the hex string.
ECDSA signatures are malleable in their ``s`` component — ``(r, s)`` and
``(r, n-s)`` both verify under the same key for the same payload but
encode to different hex. Key any such structure by
``sha256(payload) + key_fingerprint`` instead.
"""
from __future__ import annotations

import string


TRAILER_PREFIX = b"# checkov-digest: "

# DER ECDSA-P256 signatures are 70-72 bytes when r and s are full-length,
# and can drop to ~63 bytes when leading-zero stripping shortens r or s.
# 63 bytes = 126 hex chars; 72 bytes = 144 hex chars. The bounds reject
# absurd-length payloads cheaply, before any crypto.
_HEX_MIN = 126
_HEX_MAX = 144

# Uppercase hex is rejected — formatters do not normalise hex case, so
# accepting both halves would broaden the parser surface for no gain.
_LOWERCASE_HEX_BYTES = frozenset((string.digits + "abcdef").encode("ascii"))


def parse_trailer(file_bytes: bytes) -> "tuple[bytes, bytes] | None":
    """Parse a trailer-signed file's bytes into ``(signed_bytes, hex_payload)``.

    Returns ``None`` on any structural failure:

    * file does not end with exactly one ``\\n``
    * last line does not start with :data:`TRAILER_PREFIX`
    * hex payload length is outside ``[126, 144]``
    * hex payload contains any non-lowercase-hex byte

    On success, ``signed_bytes`` are the bytes to feed to SHA-256 and
    ``hex_payload`` is the lowercase-hex ASCII bytes to decode as a DER
    signature.

    A one-line trailer-only file (an empty ``__init__.py`` signed as a
    comment-only file) returns ``(b"", hex_payload)``.
    """
    if not file_bytes:
        return None
    if not file_bytes.endswith(b"\n"):
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
    """True iff the file's last ``\\n``-terminated line starts with the trailer prefix.

    Used by the verifier to split a ``parse_trailer`` ``None`` return
    into "no trailer at all" vs "trailer present but malformed", which
    drive different result codes (``NO_SIGNATURE`` vs ``BAD_SIGNATURE``).
    """
    if not file_bytes or not file_bytes.endswith(b"\n"):
        return False
    body = file_bytes[:-1]
    last_nl = body.rfind(b"\n")
    return body[last_nl + 1:].startswith(TRAILER_PREFIX)


def decode_hex_signature(hex_payload: bytes) -> "bytes | None":
    """Decode a hex-payload bytes string into raw DER signature bytes.

    Returns ``None`` on decode failure. Assumes the input already passed
    :func:`parse_trailer`'s guards; centralises the ``bytes.fromhex``
    error catching so callers don't sprinkle ``try`` blocks around.
    """
    try:
        return bytes.fromhex(hex_payload.decode("ascii"))
    except (UnicodeDecodeError, ValueError):
        return None


__all__ = [
    "TRAILER_PREFIX",
    "decode_hex_signature",
    "has_trailer_prefix",
    "parse_trailer",
]
