"""External-checks signature verification.

Public surface is lazily re-exported via PEP 562 ``__getattr__``.

**Why lazy?** The legacy code path
(``BaseCheckRegistry.load_external_checks`` with no public key
configured) must work on installs without ``cryptography`` installed —
``cryptography`` is NOT a core checkov dependency, it is only required
when the operator opts into verification. Eager re-exports of the
crypto-touching submodules (``keys``, ``verifier``, ``enforce``)
would break every existing user of ``--external-checks-dir`` with
``ModuleNotFoundError: No module named 'cryptography'`` on a stock
install. The PEP 562 hook resolves symbols on first access, so the
package import is side-effect free.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any


__all__ = [
    "LOADABLE_SUFFIXES",
    "SignatureVerificationError",
    "TRAILER_PREFIX",
    "VerificationKey",
    "VerificationResult",
    "has_double_trailer",
    "load_public_keys",
    "verify_bytes",
    "verify_external_checks_dirs",
    "verify_file",
]


# public name -> (submodule, attribute)
_LAZY_EXPORTS: "dict[str, tuple[str, str]]" = {
    "LOADABLE_SUFFIXES":           ("enforce",        "LOADABLE_SUFFIXES"),
    "verify_external_checks_dirs": ("enforce",        "verify_external_checks_dirs"),
    "SignatureVerificationError":  ("errors",         "SignatureVerificationError"),
    "VerificationKey":             ("keys",           "VerificationKey"),
    "load_public_keys":            ("keys",           "load_public_keys"),
    "TRAILER_PREFIX":              ("trailer_format", "TRAILER_PREFIX"),
    "has_double_trailer":          ("trailer_format", "has_double_trailer"),
    "VerificationResult":          ("verifier",       "VerificationResult"),
    "verify_bytes":                ("verifier",       "verify_bytes"),
    "verify_file":                 ("verifier",       "verify_file"),
}


def __getattr__(name: str) -> Any:
    target = _LAZY_EXPORTS.get(name)
    if target is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    submodule_name, attribute_name = target
    import importlib
    submodule = importlib.import_module(f"{__name__}.{submodule_name}")
    value = getattr(submodule, attribute_name)
    globals()[name] = value  # cache for subsequent lookups
    return value


def __dir__() -> "list[str]":
    return sorted(list(globals().keys()) + list(_LAZY_EXPORTS.keys()))


if TYPE_CHECKING:
    from .enforce import LOADABLE_SUFFIXES, verify_external_checks_dirs
    from .errors import SignatureVerificationError
    from .keys import VerificationKey, load_public_keys
    from .trailer_format import TRAILER_PREFIX, has_double_trailer
    from .verifier import VerificationResult, verify_bytes, verify_file
