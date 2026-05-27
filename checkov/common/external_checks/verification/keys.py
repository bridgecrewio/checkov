"""Public-key loading. Only ECDSA P-256 + SHA-256 is accepted."""
from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass

from ecdsa import NIST256p, VerifyingKey
from ecdsa.errors import MalformedPointError

from .errors import SignatureVerificationError


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class VerificationKey:
    public_key: VerifyingKey
    fingerprint_hex: str
    source_path: str


def _validate_curve(vk: VerifyingKey, source_path: str) -> VerifyingKey:
    if vk.curve != NIST256p:
        raise SignatureVerificationError(f"unsupported key format in {source_path}")
    return vk


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

        try:
            vk = VerifyingKey.from_pem(pem)
        except (MalformedPointError, ValueError, TypeError, Exception) as exc:
            # ``ecdsa`` raises a wide assortment (UnexpectedDER, base64,
            # plain Exception); collapse them all to one consistent error.
            raise SignatureVerificationError(f"unsupported key format in {path}") from exc

        validated = _validate_curve(vk, path)
        spki_der = validated.to_der()  # SPKI DER form
        fingerprint = hashlib.sha256(spki_der).hexdigest()
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
