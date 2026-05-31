from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
from pathlib import Path
from typing import Callable

import pytest
from ecdsa import NIST256p, SigningKey
from ecdsa.util import sigencode_der

# ──────────────────────────────────────────────────────────────────────────────
# xdist single-worker pinning for this package.
#
# Why: the unit-tests(3.9) GitHub Actions job intermittently crashed with
# `Fatal Python error: Segmentation fault` inside `posixpath.realpath`, called
# from pytest's `tmp_path` fixture on the *other* xdist worker (not in any
# test from this package). Locally on Python 3.12 the same `-n 2 --dist
# loadfile` config runs the whole 3914-test suite with zero segfaults — the
# crash is a Python-3.9- and ubuntu-runner-specific race, most likely between
# a C extension's worker thread (pycares / aiodns / aiohttp transitive dep)
# and our `tmp_path`-heavy tests on the other xdist worker.
#
# Fix: attach `xdist_group("external_checks_verification")` to every test
# collected from this package so xdist's `LoadGroupScheduling` (enabled via
# `--dist loadgroup` in pyproject.toml) pins them all onto a single worker.
# This serialises this package's tests with whatever else lands on that
# worker through the GIL, eliminating the cross-process race window.
#
# Caveats:
# - `pytest_collection_modifyitems` defined in a conftest receives ALL
#   collected items (not just items in the conftest's subtree) — we must
#   filter by nodeid prefix.
# - `tryfirst=True` ensures we add the mark BEFORE xdist's own
#   `pytest_collection_modifyitems` (in `xdist/remote.py`) reads it and
#   appends the `@<group>` suffix to `item._nodeid` that LoadGroupScheduling
#   actually keys on.
# ──────────────────────────────────────────────────────────────────────────────
_VERIFICATION_PKG_PREFIX = "tests/common/external_checks/verification/"
_XDIST_GROUP = "external_checks_verification"


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Attach `xdist_group(_XDIST_GROUP)` to every test in this package so
    `--dist loadgroup` schedules them on a single xdist worker.

    See the block comment above for the segfault background and the rationale
    for `tryfirst=True` / the nodeid-prefix filter.
    """
    mark = pytest.mark.xdist_group(_XDIST_GROUP)
    for item in items:
        # `nodeid` uses forward slashes on every platform — safe to substring-match.
        if item.nodeid.startswith(_VERIFICATION_PKG_PREFIX):
            item.add_marker(mark)


def _gen_p256_pem() -> tuple[bytes, SigningKey]:
    """Return ``(public_key_pem_bytes, private_key_object)`` for a fresh P-256 key."""
    priv = SigningKey.generate(curve=NIST256p)
    pub_pem = priv.get_verifying_key().to_pem()
    return pub_pem, priv


def _sign_p256(priv: SigningKey, payload: bytes) -> bytes:
    """Produce a DER ECDSA-SHA256 signature over ``payload``."""
    return priv.sign_deterministic(
        payload, hashfunc=hashlib.sha256, sigencode=sigencode_der,
    )


def _append_trailer(body: bytes, priv: SigningKey) -> bytes:
    """Return ``body + b"# checkov-digest: <hex>\\n"`` ready to write to disk."""
    sig_der = _sign_p256(priv, body)
    return body + b"# checkov-digest: " + sig_der.hex().encode("ascii") + b"\n"


@pytest.fixture(scope="session")
def keypair_a() -> tuple[bytes, SigningKey]:
    return _gen_p256_pem()


@pytest.fixture(scope="session")
def keypair_b() -> tuple[bytes, SigningKey]:
    return _gen_p256_pem()


@pytest.fixture(scope="session")
def key_a_pub_pem(keypair_a) -> bytes:
    return keypair_a[0]


@pytest.fixture(scope="session")
def key_b_pub_pem(keypair_b) -> bytes:
    return keypair_b[0]


@pytest.fixture(scope="session")
def priv_a(keypair_a) -> SigningKey:
    return keypair_a[1]


@pytest.fixture(scope="session")
def priv_b(keypair_b) -> SigningKey:
    return keypair_b[1]


# --- Unsupported-key-format fixtures ---------------------------------------

def _openssl_or_skip() -> str:
    path = shutil.which("openssl")
    if path is None:
        pytest.skip("openssl CLI not installed", allow_module_level=False)
    return path


def _openssl_pubkey_pem(genpkey_args: "list[str]") -> bytes:
    """Run ``openssl genpkey <args>`` + ``openssl pkey -pubout``.

    Skips the requesting test (instead of failing it) when the local
    ``openssl`` build does not support the requested algorithm — older
    LibreSSL / system-shipped OpenSSL builds lack ED25519 or specific
    EC curves. Operators who run the suite in a minimal CI image should
    see clean ``SKIPPED`` entries, not red errors.
    """
    openssl = _openssl_or_skip()
    priv_proc = subprocess.run(
        [openssl, "genpkey"] + genpkey_args,
        capture_output=True, check=False,
    )
    if priv_proc.returncode != 0:
        stderr = (priv_proc.stderr or b"").decode("utf-8", errors="replace")
        pytest.skip(
            f"openssl genpkey {' '.join(genpkey_args)!r} not supported "
            f"by this openssl build: {stderr.strip()}"
        )
    pub = subprocess.run(
        [openssl, "pkey", "-pubout"], input=priv_proc.stdout,
        capture_output=True, check=True,
    ).stdout
    return pub


def _rsa_pub_pem() -> bytes:
    return _openssl_pubkey_pem(["-algorithm", "RSA", "-pkeyopt", "rsa_keygen_bits:2048"])


def _ed25519_pub_pem() -> bytes:
    return _openssl_pubkey_pem(["-algorithm", "ED25519"])


def _p384_pub_pem() -> bytes:
    return _openssl_pubkey_pem(["-algorithm", "EC", "-pkeyopt", "ec_paramgen_curve:P-384"])


def _secp256k1_pub_pem() -> bytes:
    """SECP256K1 (Bitcoin) public key — the curve operators are most
    likely to accidentally use because it shows up in countless ECDSA
    tutorials and Stack Overflow answers. Built via the legacy
    ``openssl ecparam ... -genkey`` recipe (``genpkey`` does not
    accept ``secp256k1`` on every openssl build).
    """
    openssl = _openssl_or_skip()
    priv_proc = subprocess.run(
        [openssl, "ecparam", "-name", "secp256k1", "-genkey", "-noout"],
        capture_output=True, check=False,
    )
    if priv_proc.returncode != 0:
        stderr = (priv_proc.stderr or b"").decode("utf-8", errors="replace")
        pytest.skip(f"openssl build lacks secp256k1: {stderr.strip()}")
    pub_proc = subprocess.run(
        [openssl, "ec", "-pubout"], input=priv_proc.stdout,
        capture_output=True, check=False,
    )
    if pub_proc.returncode != 0:
        stderr = (pub_proc.stderr or b"").decode("utf-8", errors="replace")
        pytest.skip(f"openssl ec -pubout failed for secp256k1: {stderr.strip()}")
    return pub_proc.stdout


@pytest.fixture(scope="session")
def unsupported_key_format_a() -> bytes:
    return _rsa_pub_pem()


@pytest.fixture(scope="session")
def unsupported_key_format_b() -> bytes:
    return _ed25519_pub_pem()


@pytest.fixture(scope="session")
def unsupported_key_format_c() -> bytes:
    return _p384_pub_pem()


@pytest.fixture(scope="session")
def unsupported_key_format_d() -> bytes:
    """SECP256K1 (Bitcoin curve) — the curve operators are most likely
    to accidentally use. Skipped when the local openssl build lacks
    secp256k1 support."""
    return _secp256k1_pub_pem()


@pytest.fixture(scope="session")
def unsupported_key_format_e() -> bytes:
    """P-521 — a NIST EC curve that looks superficially like P-256
    but has a different key size, so the loader must reject it."""
    return _openssl_pubkey_pem(["-algorithm", "EC", "-pkeyopt", "ec_paramgen_curve:P-521"])


@pytest.fixture
def make_sign() -> Callable[[SigningKey, bytes], bytes]:
    """Return a callable that produces a DER signature over given bytes."""
    return _sign_p256


@pytest.fixture
def make_trailer() -> Callable[[bytes, SigningKey], bytes]:
    """Return a callable that returns ``body + trailer-line`` for any body+key."""
    return _append_trailer


# Canonical pre-trailer bodies for ``valid_dir`` — module-level so tests
# can compare the verifier's returned bytes against the originals.
_VALID_BODIES: "dict[str, bytes]" = {
    "__init__.py": b"",
    "aws_check.py": b"# valid check\nCHECK_ID = 'CKV_T_1'\n",
    "_helper.py": (
        b"# helper module\n"
        b"HELPER = True\n"
        + b"# padding line\n" * 200
    ),
}


@pytest.fixture
def valid_bodies() -> "dict[str, bytes]":
    return dict(_VALID_BODIES)


@pytest.fixture
def valid_dir(tmp_path: Path, priv_a) -> Path:
    """Directory with every ``.py`` file trailer-signed by ``priv_a``."""
    root = tmp_path / "valid"
    root.mkdir()
    for name, body in _VALID_BODIES.items():
        (root / name).write_bytes(_append_trailer(body, priv_a))
    return root


@pytest.fixture
def mutated_dir(valid_dir: Path) -> Path:
    """One file in the valid dir has had a stray line appended after the trailer."""
    target = valid_dir / "aws_check.py"
    target.write_bytes(target.read_bytes() + b"# extra\n")
    return valid_dir


@pytest.fixture
def unsigned_dir(tmp_path: Path) -> Path:
    """Directory with Python files but no trailer lines at all."""
    root = tmp_path / "unsigned"
    root.mkdir()
    (root / "__init__.py").write_bytes(b"")
    (root / "aws_check.py").write_bytes(b"# unsigned\nCHECK_ID = 'CKV_T_1'\n")
    return root


@pytest.fixture
def partial_dir(tmp_path: Path, priv_a) -> Path:
    """One signed ``.py`` and an unsigned ``__init__.py`` (a real loader path)."""
    root = tmp_path / "partial"
    root.mkdir()
    signed_body = b"# signed\nCHECK_ID = 'CKV_T_1'\n"
    (root / "aws_check.py").write_bytes(_append_trailer(signed_body, priv_a))
    (root / "__init__.py").write_bytes(b"")
    return root


@pytest.fixture
def platform_style_dir(tmp_path: Path) -> Path:
    """Mimics a platform-supplied policies directory (YAML only, no .py)."""
    root = tmp_path / "platform"
    root.mkdir()
    (root / "policy_1.yaml").write_bytes(b"id: CKV_T_2\nseverity: HIGH\n")
    (root / "policy_2.yaml").write_bytes(b"id: CKV_T_3\nseverity: LOW\n")
    return root


@pytest.fixture
def mixed_dir(valid_dir: Path) -> Path:
    """Valid signed dir plus non-Python text files the verifier should ignore."""
    (valid_dir / "README.md").write_bytes(b"# Docs\n")
    (valid_dir / "checks.yaml").write_bytes(b"id: CKV_T_4\n")
    (valid_dir / "LICENSE").write_bytes(b"Apache 2.0\n")
    return valid_dir


@pytest.fixture
def link_escape_dir(tmp_path: Path, priv_a) -> Path:
    """Directory with a symlink that resolves outside the tree.

    Skipped on platforms where symlinks aren't supported.
    """
    outside = tmp_path / "outside"
    outside.mkdir()
    payload = outside / "outside_module.py"
    payload.write_bytes(b"# code outside the verified tree\n")

    root = tmp_path / "with_link"
    root.mkdir()
    (root / "__init__.py").write_bytes(_append_trailer(b"", priv_a))
    (root / "inside.py").write_bytes(_append_trailer(b"# inside check\n", priv_a))

    link = root / "looks_local.py"
    try:
        os.symlink(payload, link)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks not supported on this platform")
    return root


@pytest.fixture
def binary_loadable_dir(tmp_path: Path, priv_a) -> Path:
    """Valid signed ``.py`` ready for a test to drop a binary loadable file into."""
    root = tmp_path / "binary"
    root.mkdir()
    (root / "aws_check.py").write_bytes(_append_trailer(b"# valid\n", priv_a))
    return root


# --- Shared test scaffolding -----------------------------------------------

@pytest.fixture(scope="session")
def stub_registry_cls():
    """Concrete ``BaseCheckRegistry`` for tests that just need a loadable
    instance (the abstract ``extract_entity_details`` is never called in
    the loader/registry paths under test)."""
    from checkov.common.checks.base_check_registry import BaseCheckRegistry

    class _StubRegistry(BaseCheckRegistry):
        def extract_entity_details(self, entity):
            return ("", "", {})

    return _StubRegistry


@pytest.fixture
def stub_registry(stub_registry_cls):
    """Pre-built ``_StubRegistry(report_type="terraform")`` instance."""
    return stub_registry_cls(report_type="terraform")


@pytest.fixture
def make_checkov():
    """Build a ``Checkov`` skeleton exposing only what the chokepoint reads.

    Usage:
        checkov = make_checkov(
            external_checks_dir=[str(some_dir)],
            external_checks_public_key=[str(key_path)],
        )
    """
    import types
    from checkov.main import Checkov

    def _build(
        *,
        external_checks_dir=None,
        external_checks_public_key=None,
        external_checks_git=None,
        no_fail_on_crash=False,
    ):
        instance = Checkov.__new__(Checkov)
        instance.config = types.SimpleNamespace(  # type: ignore[attr-defined]
            external_checks_dir=external_checks_dir,
            external_checks_public_key=external_checks_public_key,
            external_checks_git=external_checks_git,
            no_fail_on_crash=no_fail_on_crash,
        )
        return instance

    return _build
