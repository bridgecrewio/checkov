"""Single-file ECDSA-P256-SHA256 trailer verification."""
from __future__ import annotations

import enum
import hashlib
import logging
from typing import Iterable

# ``ecdsa`` is an optional dependency (the ``signed-checks`` extra); every
# primitive is resolved through the lazy ``_ecdsa`` accessor so that
# ``import checkov`` stays free of it.
from . import _ecdsa
from .keys import VerificationKey
from .trailer_format import (
    decode_hex_signature,
    has_double_trailer,
    has_trailer_prefix,
    parse_trailer,
)


logger = logging.getLogger(__name__)


class VerificationResult(enum.Enum):
    OK = "ok"
    NO_SIGNATURE = "no_signature"
    BAD_SIGNATURE = "bad_signature"
    UNKNOWN_KEY = "unknown_key"
    IO_ERROR = "io_error"
    DOUBLE_TRAILER = "double_trailer"


def _signature_is_well_formed(sig_der: bytes) -> bool:
    """Strict-DER decode plus ECDSA ``[1, n-1]`` range check on ``r`` and ``s``."""
    order = _ecdsa.secp256r1_order()
    try:
        r, s = _ecdsa.sigdecode_der()(sig_der, order)
    except Exception:
        return False
    if r <= 0 or r >= order:
        return False
    if s <= 0 or s >= order:
        return False
    return True


def _verify_against_keys(
    payload: bytes,
    sig_der: bytes,
    keys: "Iterable[VerificationKey]",
) -> VerificationResult:
    expected_errors = _ecdsa.verify_error_types()
    sigdecode = _ecdsa.sigdecode_der()
    for key in keys:
        try:
            key.public_key.verify(
                sig_der, payload, hashfunc=hashlib.sha256, sigdecode=sigdecode,
            )
            return VerificationResult.OK
        except expected_errors:
            continue
    return VerificationResult.UNKNOWN_KEY


def verify_bytes(
    file_bytes: bytes,
    keys: "Iterable[VerificationKey]",
) -> "tuple[VerificationResult, bytes]":
    """Verify in-memory trailer-signed bytes; ``signed_bytes`` is ``b""`` on non-OK."""
    keys_list = list(keys)
    if not keys_list:
        raise ValueError("verify_bytes requires at least one key")

    if has_double_trailer(file_bytes):
        return VerificationResult.DOUBLE_TRAILER, b""

    parsed = parse_trailer(file_bytes)
    if parsed is None:
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
