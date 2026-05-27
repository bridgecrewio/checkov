from __future__ import annotations

import enum
import hashlib
import logging
from typing import Iterable

from ecdsa import BadSignatureError, NIST256p
from ecdsa.util import sigdecode_der

from .keys import VerificationKey
from .trailer_format import (
    decode_hex_signature,
    has_double_trailer,
    has_trailer_prefix,
    parse_trailer,
)


logger = logging.getLogger(__name__)


# secp256r1 group order (SEC 2 §2.4.2 / RFC 5480 §2.1.1.1).
_SECP256R1_N = NIST256p.order


class VerificationResult(enum.Enum):
    OK = "ok"
    NO_SIGNATURE = "no_signature"
    BAD_SIGNATURE = "bad_signature"
    UNKNOWN_KEY = "unknown_key"
    IO_ERROR = "io_error"
    DOUBLE_TRAILER = "double_trailer"


def _signature_is_well_formed(sig_der: bytes) -> bool:
    """Strict-DER decode plus ECDSA ``[1, n-1]`` range check on ``r`` and ``s``."""
    try:
        r, s = sigdecode_der(sig_der, _SECP256R1_N)
    except Exception:
        # ``ecdsa.util.sigdecode_der`` raises a variety: UnexpectedDER,
        # ValueError, IndexError. Collapse to a single boolean here.
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
            key.public_key.verify(
                sig_der, payload, hashfunc=hashlib.sha256, sigdecode=sigdecode_der,
            )
            return VerificationResult.OK
        except BadSignatureError:
            continue
        except Exception:
            # Malformed DER caught upstream by _signature_is_well_formed,
            # but defend against the ecdsa lib raising for any other reason.
            continue
    return VerificationResult.UNKNOWN_KEY


def verify_bytes(
    file_bytes: bytes,
    keys: "Iterable[VerificationKey]",
) -> "tuple[VerificationResult, bytes]":
    """Verify in-memory trailer-signed bytes.

    Returns ``(result, signed_bytes)``; ``signed_bytes`` is ``b""`` on
    any non-OK result. Raises :class:`ValueError` if ``keys`` is empty.
    """
    keys_list = list(keys)
    if not keys_list:
        raise ValueError("verify_bytes requires at least one key")

    if has_double_trailer(file_bytes):
        return VerificationResult.DOUBLE_TRAILER, b""

    parsed = parse_trailer(file_bytes)
    if parsed is None:
        # Distinguish "no trailer" from "malformed trailer" for error messages.
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
