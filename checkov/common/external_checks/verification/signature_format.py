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


def sidecar_path_for(payload_path: str) -> str:
    """Return the path of the ``.sig`` sidecar for a payload file."""
    return payload_path + SIG_SUFFIX


def read_signature(sig_path: str) -> bytes:
    """Read the raw DER signature bytes from disk."""
    with open(sig_path, "rb") as f:
        return f.read()


__all__ = ["SIG_SUFFIX", "read_signature", "sidecar_path_for"]
