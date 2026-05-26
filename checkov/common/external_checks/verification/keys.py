"""Public-key loading and primitive pinning.

Only ECDSA over NIST P-256 (``secp256r1``) with SHA-256 is accepted; any
other curve or key type is rejected at load time so operator
misconfiguration fails fast.
"""
from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePublicKey, SECP256R1

from .errors import SignatureVerificationError


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class VerificationKey:
    """A loaded P-256 public key with its SHA-256 SPKI fingerprint."""
    public_key: EllipticCurvePublicKey
    fingerprint_hex: str
    source_path: str


def _validate_curve(pub: object, source_path: str) -> EllipticCurvePublicKey:
    if not isinstance(pub, EllipticCurvePublicKey) or not isinstance(pub.curve, SECP256R1):
        raise SignatureVerificationError(f"unsupported key format in {source_path}")
    return pub


def load_public_keys(paths: "list[str]") -> "list[VerificationKey]":
    """Read PEM-encoded P-256 public keys from disk and validate each one.

    Raises :class:`SignatureVerificationError` on any read or parse failure.
    """
    keys: "list[VerificationKey]" = []
    for path in paths:
        try:
            with open(path, "rb") as f:
                pem = f.read()
        except OSError as exc:
            raise SignatureVerificationError(
                f"cannot read public key {path}: {exc.strerror or exc}"
            ) from exc

        try:
            pub = serialization.load_pem_public_key(pem)
        except (ValueError, TypeError) as exc:
            raise SignatureVerificationError(f"unsupported key format in {path}") from exc

        validated = _validate_curve(pub, path)
        spki = validated.public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        fingerprint = hashlib.sha256(spki).hexdigest()
        keys.append(VerificationKey(
            public_key=validated,
            fingerprint_hex=fingerprint,
            source_path=path,
        ))
        logger.debug("Loaded verification key %s (fp=%s)", path, fingerprint[:16])

    return keys


__all__ = [
    "SignatureVerificationError",
    "VerificationKey",
    "load_public_keys",
]
