"""Public-key loading. Only ECDSA P-256 + SHA-256 is accepted."""
from __future__ import annotations

import binascii
import hashlib
import logging
from dataclasses import dataclass

# ecdsa ships no py.typed marker; suppress the strict-mode import-untyped
# noise here rather than polluting mypy.ini for a single MR-scoped dependency.
from ecdsa import NIST256p, VerifyingKey  # type: ignore[import-untyped]
from ecdsa.der import UnexpectedDER  # type: ignore[import-untyped]
from ecdsa.errors import MalformedPointError  # type: ignore[import-untyped]

from .errors import SignatureVerificationError


logger = logging.getLogger(__name__)


# Anything outside this set propagates so unrelated bugs surface with their real root cause.
_EXPECTED_PEM_LOAD_ERRORS = (
    UnexpectedDER,
    binascii.Error,
    MalformedPointError,
    ValueError,
    TypeError,
)


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
        except _EXPECTED_PEM_LOAD_ERRORS as exc:
            raise SignatureVerificationError(f"unsupported key format in {path}") from exc

        validated = _validate_curve(vk, path)
        spki_der = validated.to_der()
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
