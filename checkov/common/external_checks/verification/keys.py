"""Public-key loading and primitive pinning for external-check verification.

Only ECDSA over the NIST P-256 (``secp256r1``) curve with SHA-256 is accepted.
Any other key type or curve is rejected up-front, before any directory walk
happens, so an operator setup error fails fast and clearly.
"""
from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePublicKey, SECP256R1


logger = logging.getLogger(__name__)


class SignatureVerificationError(Exception):
    """Raised when verification fails for any reason (bad key, bad signature,
    missing signature, malformed input, or a directory that contains an
    unsigned Python-loadable file)."""


@dataclass(frozen=True)
class VerificationKey:
    """A loaded, validated P-256 public key plus its SHA-256 fingerprint.

    The fingerprint is the SHA-256 of the SubjectPublicKeyInfo DER encoding
    of the public key. It is used only for logging / diagnostic identity;
    verification itself tries each configured key in order.
    """
    public_key: EllipticCurvePublicKey
    fingerprint_hex: str
    source_path: str


def _validate_curve(pub: object, source_path: str) -> EllipticCurvePublicKey:
    if not isinstance(pub, EllipticCurvePublicKey):
        raise SignatureVerificationError(
            f"unsupported key format in {source_path}"
        )
    if not isinstance(pub.curve, SECP256R1):
        raise SignatureVerificationError(
            f"unsupported key format in {source_path}"
        )
    return pub


def load_public_keys(paths: "list[str]") -> "list[VerificationKey]":
    """Read PEM-encoded public keys from disk and validate each one.

    Raises :class:`SignatureVerificationError` if any key cannot be parsed
    or is not a P-256 ECDSA key. The error message names the offending path
    but does not enumerate which formats are rejected.
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
            raise SignatureVerificationError(
                f"unsupported key format in {path}"
            ) from exc

        validated = _validate_curve(pub, path)
        spki = validated.public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        fingerprint = hashlib.sha256(spki).hexdigest()
        keys.append(
            VerificationKey(
                public_key=validated,
                fingerprint_hex=fingerprint,
                source_path=path,
            )
        )
        logger.debug("Loaded verification key %s (fp=%s)", path, fingerprint[:16])

    return keys


__all__ = [
    "SignatureVerificationError",
    "VerificationKey",
    "load_public_keys",
]
