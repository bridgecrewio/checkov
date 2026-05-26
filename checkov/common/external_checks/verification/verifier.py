"""Single-file signature verification.

Cryptographic invariants enforced here:

* Strict DER signature decoding via ``decode_dss_signature``. Anything
  not canonically DER-encoded is rejected before any elliptic-curve
  operation. This blocks non-canonical encodings (extra leading zeros,
  mis-encoded integer lengths) that some libraries accept.
* Curve-and-key-type pinning happens at key-load time in :mod:`.keys`;
  this module trusts the caller-supplied list.
* ``r`` and ``s`` are checked against the standard ECDSA validity range
  ``[1, n-1]``. ``s`` is **not** further constrained to ``[1, n/2]``
  (the "low-S" canonical half of the curve order).

  Rationale for accepting both halves: ECDSA signatures are
  mathematically equivalent in pairs — ``(r, s)`` and ``(r, n-s)`` both
  verify the same message under the same key. The dominant signing
  tools customers use produce signatures in either half non-
  deterministically: ``openssl dgst -sha256 -sign`` and AWS KMS yield
  ``s > n/2`` roughly half the time (RFC 6979 fixes the deterministic
  selection of ``k`` but not S-normalisation), while ``cosign sign-blob``
  and GCP Cloud KMS normalise to the low half. Requiring low-S would
  reject around 50% of signatures produced by the most common workflows.

  Accepting both halves is safe in this design because:
  - The verifier reads each signature exactly once and discards it
    immediately after returning ``OK``.
  - The verified bytes returned to the loader are the payload bytes,
    not the signature bytes. Signature representation cannot influence
    which payload gets executed.
  - There is no cache, log, dedup table, replay-protection store, or
    persistent index anywhere in this package that is keyed by
    signature bytes (or any hash thereof).

  Maintenance note for future contributors: if you add such a structure
  (cache keyed by ``sha256(sig)`` is the textbook example), the
  equivalence above no longer holds and low-S enforcement must come
  back. The safer pattern is to key any such structure by
  ``sha256(payload) + key_fingerprint`` instead, which sidesteps the
  question entirely.
"""
from __future__ import annotations

import enum
import logging
import os
from dataclasses import dataclass
from typing import Iterable

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature

from .keys import VerificationKey
from .signature_format import read_signature


logger = logging.getLogger(__name__)


# secp256r1 group order; see SEC 2 §2.4.2 or RFC 5480 §2.1.1.1.
# Used only for the standard ``r, s in [1, n-1]`` validity check.
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


@dataclass(frozen=True)
class FileVerification:
    """Result plus (on ``OK``) the bytes the loader should execute.

    The verifier reads the payload bytes into memory exactly once and
    returns them alongside the result so the loader can ``exec`` from
    that buffer instead of re-reading from disk. This guarantees the
    bytes that were verified are the bytes that get executed.
    """

    result: VerificationResult
    payload_bytes: bytes = b""


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
    any_tried = False
    for key in keys:
        any_tried = True
        try:
            key.public_key.verify(sig_der, payload, ec.ECDSA(hashes.SHA256()))
            return VerificationResult.OK
        except InvalidSignature:
            continue
    if not any_tried:
        # No keys configured: caller should not have invoked us.
        return VerificationResult.UNKNOWN_KEY
    return VerificationResult.UNKNOWN_KEY


def verify_bytes(
    payload: bytes,
    sig_der: bytes,
    keys: "Iterable[VerificationKey]",
) -> VerificationResult:
    """Verify a payload+signature pair already in memory."""
    if not sig_der:
        return VerificationResult.NO_SIGNATURE
    if not _signature_is_well_formed(sig_der):
        return VerificationResult.BAD_SIGNATURE
    return _verify_against_keys(payload, sig_der, keys)


def verify_file(
    payload_path: str,
    sig_path: str,
    keys: "Iterable[VerificationKey]",
) -> VerificationResult:
    """Read ``payload_path`` and ``sig_path`` from disk and verify."""
    if not os.path.isfile(sig_path):
        return VerificationResult.NO_SIGNATURE
    try:
        sig_der = read_signature(sig_path)
    except OSError as exc:
        logger.debug("cannot read sidecar %s: %s", sig_path, exc)
        return VerificationResult.NO_SIGNATURE
    try:
        with open(payload_path, "rb") as f:
            payload = f.read()
    except OSError as exc:
        logger.debug("cannot read payload %s: %s", payload_path, exc)
        return VerificationResult.BAD_SIGNATURE
    return verify_bytes(payload, sig_der, keys)


def verify_file_with_bytes(
    payload_path: str,
    sig_path: str,
    keys: "Iterable[VerificationKey]",
) -> FileVerification:
    """Like :func:`verify_file` but also returns the payload bytes on success.

    The bytes are read exactly once. Callers that intend to load the file
    afterwards must use these bytes rather than re-reading from disk so
    the verified-bytes invariant holds end-to-end.
    """
    if not os.path.isfile(sig_path):
        return FileVerification(VerificationResult.NO_SIGNATURE)
    try:
        sig_der = read_signature(sig_path)
        with open(payload_path, "rb") as f:
            payload = f.read()
    except OSError as exc:
        logger.debug("cannot read %s or %s: %s", payload_path, sig_path, exc)
        return FileVerification(VerificationResult.NO_SIGNATURE)
    result = verify_bytes(payload, sig_der, keys)
    if result == VerificationResult.OK:
        return FileVerification(result, payload)
    return FileVerification(result)


__all__ = [
    "FileVerification",
    "VerificationResult",
    "verify_bytes",
    "verify_file",
    "verify_file_with_bytes",
]
