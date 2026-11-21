"""Public-key loading. Only ECDSA P-256 + SHA-256 is accepted."""
from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from . import _ecdsa
from .errors import SignatureVerificationError

# ``ecdsa`` is an optional dependency (the ``signed-checks`` extra), so its
# runtime import lives in ``_ecdsa``. The type-only import keeps the precise
# ``VerifyingKey`` annotation without pulling ``ecdsa`` into ``sys.modules``.
if TYPE_CHECKING:
    from ecdsa import VerifyingKey  # type: ignore[import-untyped]


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class VerificationKey:
    public_key: "VerifyingKey"
    fingerprint_hex: str
    source_path: str


def _validate_curve(vk: "VerifyingKey", source_path: str) -> "VerifyingKey":
    if vk.curve != _ecdsa.nist256p():
        raise SignatureVerificationError(f"unsupported key format in {source_path}")
    return vk


def load_public_keys(paths: "list[str]") -> "list[VerificationKey]":
    # Resolve the optional dependency before opening any file, so a missing
    # extra is reported as such rather than as a malformed key.
    _ecdsa.require()
    expected_errors = _ecdsa.pem_load_error_types()

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
            vk = _ecdsa.verifying_key_class().from_pem(pem)
        except expected_errors as exc:
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


def __getattr__(name: str) -> Any:
    """Resolve the ``ecdsa`` names this module used to expose.

    Existing tests reach for ``keys.VerifyingKey`` to patch ``from_pem``;
    resolving it here keeps that working now that ``ecdsa`` is no longer
    imported at module load.
    """
    if name == "VerifyingKey":
        return _ecdsa.verifying_key_class()
    if name == "NIST256p":
        return _ecdsa.nist256p()
    raise AttributeError(name)


__all__ = [
    "VerificationKey",
    "load_public_keys",
]
