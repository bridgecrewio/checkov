"""Single access point for the optional ``ecdsa`` dependency.

Signature verification is opt-in behind ``--external-checks-public-key``, and
``ecdsa`` is the only dependency that feature adds. ``ecdsa`` still ships
CVE-2024-23342 (the Minerva timing attack on P-256) and python-ecdsa considers
side channels out of scope, so no fixed release is coming: every dependency
scanner flags a default Checkov install for a code path most users never run.
It therefore lives in the ``signed-checks`` extra, and this module is the only
place allowed to import it.

Everything is resolved lazily: ``import checkov`` must not put ``ecdsa`` into
``sys.modules``. Each helper below is called from inside the verification
functions, so a plain scan never pays for the import.
"""
from __future__ import annotations

import importlib
from typing import Any

_INSTALL_HINT = (
    "Signed external-check verification needs the optional 'ecdsa' dependency, "
    "which is not installed. Install it with 'pip install checkov[signed-checks]' "
    "(or 'pip install \"ecdsa>=0.19.0,<1.0.0\"') and re-run, or drop "
    "--external-checks-public-key to load external checks unverified."
)

_ECDSA_MODULE = "ecdsa"

_module: "Any | None" = None


def _import_ecdsa() -> Any:
    """Import ``ecdsa`` once and cache it; raise ``ImportError`` when missing."""
    global _module
    if _module is None:
        _module = importlib.import_module(_ECDSA_MODULE)
    return _module


def is_available() -> bool:
    """True when ``ecdsa`` can be imported; never raises."""
    try:
        _import_ecdsa()
        return True
    except ImportError:
        return False


def require() -> Any:
    """Return the ``ecdsa`` module, or raise the install hint.

    The raised type is ``SignatureVerificationError`` so the verification
    chokepoint in ``checkov/main.py`` reports it and exits with the documented
    code instead of surfacing a bare ``ModuleNotFoundError``.
    """
    try:
        return _import_ecdsa()
    except ImportError as exc:
        # Imported here: ``errors`` stays dependency-free, which matters
        # because it is loaded by the crash-handling path itself.
        from .errors import SignatureVerificationError

        raise SignatureVerificationError(_INSTALL_HINT) from exc


def _submodule(name: str) -> Any:
    return importlib.import_module(f"{_ECDSA_MODULE}.{name}")


def nist256p() -> Any:
    """The P-256 curve object (``ecdsa.NIST256p``)."""
    return require().NIST256p


def verifying_key_class() -> Any:
    """``ecdsa.VerifyingKey``; PEM keys are parsed through it."""
    return require().VerifyingKey


def secp256r1_order() -> int:
    """P-256 group order, used for the strict DER ``r``/``s`` range check."""
    return int(require().NIST256p.order)


def sigdecode_der() -> Any:
    """``ecdsa.util.sigdecode_der`` — strict-DER signature decoder."""
    return _submodule("util").sigdecode_der


def pem_load_error_types() -> "tuple[type[BaseException], ...]":
    """Exceptions that mean "this PEM is not a usable P-256 SPKI".

    Anything outside this tuple propagates, so an unexpected failure keeps
    its real root cause instead of being relabelled as a bad key format.
    """
    import binascii

    return (
        _submodule("der").UnexpectedDER,
        binascii.Error,
        _submodule("errors").MalformedPointError,
        ValueError,
        TypeError,
    )


def verify_error_types() -> "tuple[type[BaseException], ...]":
    """Rejections that mean "this key did not sign the payload"."""
    return (
        require().BadSignatureError,
        _submodule("der").UnexpectedDER,
        _submodule("errors").MalformedPointError,
        ValueError,
    )


__all__ = [
    "is_available",
    "nist256p",
    "pem_load_error_types",
    "require",
    "secp256r1_order",
    "sigdecode_der",
    "verify_error_types",
    "verifying_key_class",
]
