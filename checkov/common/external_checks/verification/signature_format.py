"""On-disk signature container.

The sidecar ``<file>.sig`` is the raw DER ECDSA signature produced by:

    openssl dgst -sha256 -sign priv.pem -out check.py.sig check.py

The file contains no header, no fingerprint, no extra framing — just the
DER signature bytes. This is the exact wire format produced by ``openssl
dgst -sign``, AWS KMS ``Sign`` with ``SigningAlgorithm=ECDSA_SHA_256``,
GCP KMS asymmetric-sign for P-256, ``cosign sign-blob``, and any
PKCS#11 HSM SDK. No custom container = no custom parser bugs and no
customer-side tooling required.
"""
from __future__ import annotations

SIG_SUFFIX = ".sig"

# DER ECDSA-P256 signatures are at most ~72 bytes. The cap is well above
# any legitimate signature and well below anything that costs memory. If
# the sidecar exceeds the cap we read one byte past it so the caller can
# distinguish "exactly at the cap" (unlikely-but-OK) from "over the cap"
# (definitely malformed or hostile, fail closed).
_SIG_MAX_BYTES = 1024


class SignatureTooLargeError(Exception):
    """Sidecar exceeded the maximum allowed size."""


def sidecar_path_for(payload_path: str) -> str:
    """Return the path of the ``.sig`` sidecar for a payload file."""
    return payload_path + SIG_SUFFIX


def read_signature(sig_path: str) -> bytes:
    """Read the raw DER signature bytes from disk.

    Reads at most ``_SIG_MAX_BYTES + 1`` bytes; if the sidecar contains
    more, raises :class:`SignatureTooLargeError`. This is purely a DoS
    guard — a sidecar at /dev/zero or a multi-GB attacker-supplied file
    would otherwise OOM the verifier.
    """
    with open(sig_path, "rb") as f:
        data = f.read(_SIG_MAX_BYTES + 1)
    if len(data) > _SIG_MAX_BYTES:
        raise SignatureTooLargeError(
            f"signature sidecar {sig_path} exceeds {_SIG_MAX_BYTES}-byte limit"
        )
    return data


__all__ = [
    "SIG_SUFFIX",
    "SignatureTooLargeError",
    "read_signature",
    "sidecar_path_for",
]
