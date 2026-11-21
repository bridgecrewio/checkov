"""Public-key loading. Only ECDSA P-256 + SHA-256 is accepted."""
from __future__ import annotations

import binascii
import hashlib
import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from cryptography.exceptions import UnsupportedAlgorithm
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PublicFormat,
    load_pem_public_key,
)

from .errors import SignatureVerificationError

if TYPE_CHECKING:
    from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePublicKey


logger = logging.getLogger(__name__)


# Anything outside this set propagates so unrelated bugs surface with their real root cause.
_EXPECTED_PEM_LOAD_ERRORS = (
    binascii.Error,
    ValueError,
    TypeError,
    UnsupportedAlgorithm,
)


@dataclass(frozen=True)
class VerificationKey:
    public_key: EllipticCurvePublicKey
    fingerprint_hex: str
    source_path: str


def _validate_curve(pk: Any, source_path: str) -> EllipticCurvePublicKey:
    if not isinstance(pk, ec.EllipticCurvePublicKey) or not isinstance(pk.curve, ec.SECP256R1):
        raise SignatureVerificationError(f"unsupported key format in {source_path}")
    return pk


def load_public_keys(paths: "list[str]") -> "list[VerificationKey]":
    keys: "list[VerificationKey]" = []
    for path in paths:
        try:
            with open(path, "rb") as f:
                pem = f.read()
        except OSError as exc:
            raise SignatureVerificationError(
                f"cannot read public key {path}: {exc.strerror or exc}"
            ) from exc

        # Normalize legacy EC PUBLIC KEY banner to standard PUBLIC KEY if body is SPKI
        if b"BEGIN EC PUBLIC KEY" in pem:
            pem = pem.replace(b"BEGIN EC PUBLIC KEY", b"BEGIN PUBLIC KEY").replace(
                b"END EC PUBLIC KEY", b"END PUBLIC KEY"
            )

        try:
            pk = load_pem_public_key(pem)
        except _EXPECTED_PEM_LOAD_ERRORS as exc:
            raise SignatureVerificationError(f"unsupported key format in {path}") from exc

        validated = _validate_curve(pk, path)
        spki_der = validated.public_bytes(Encoding.DER, PublicFormat.SubjectPublicKeyInfo)
        fingerprint = hashlib.sha256(spki_der).hexdigest()
        keys.append(VerificationKey(
            public_key=validated,
            fingerprint_hex=fingerprint,
            source_path=path,
        ))
        logger.debug("Loaded verification key %s (fp=%s)", path, fingerprint[:16])

    return keys


__all__ = [
    "VerificationKey",
    "load_public_keys",
]
