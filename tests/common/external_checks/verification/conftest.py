from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Callable

import pytest
from ecdsa import NIST256p, SigningKey
from ecdsa.util import sigencode_der


# ──────────────────────────────────────────────────────────────────────────────
# Python 3.9 / 3.10 stability — run each verification test in a forked
# subprocess.
#
# Under Python 3.9 and 3.10 + xdist on Linux, ``pytest``'s ``tmp_path``
# fixture segfaults the worker inside ``posixpath.realpath`` for some
# verification tests. Verified via CI traceback on both versions:
#
#   Current thread <id> (most recent call first):
#     File "posixpath.py", line 393 in realpath
#     File "pathlib.py", ... in resolve
#     File "_pytest/tmpdir.py", line 116 in _ensure_relative_to_basetemp
#     ...
#
# The traceback also shows a parked ``pycares._run_safe_shutdown_loop``
# thread, but disabling pycares does NOT fix the crash, so pycares is
# not the racer.
#
# When the worker dies mid-test under ``--dist loadfile``, the xdist
# controller's ``loop_once`` blocks in ``queue.get()`` forever (the dead
# worker's test results never arrive and the file is never reassigned),
# which turns a single-test crash into a full job-timeout hang.
#
# Running each test in a forked subprocess (via ``pytest-forked``)
# isolates the crash: a SIGSEGV kills only the fork, the parent worker
# stays alive, and the test surfaces as a normal failure instead of
# hanging the whole job. Python 3.11+ doesn't exhibit the crash, so the
# mark is gated on the interpreter version.
if sys.version_info < (3, 11):
    # IMPORTANT: this hook fires with the FULL session ``items`` list,
    # not just items collected under this directory. We must filter by
    # the test's file path so the ``forked`` marker is applied only to
    # verification tests; otherwise every test in the suite runs in its
    # own subprocess and loses class-level state from earlier tests in
    # the same file (which broke ``tests/common/integration_features/
    # test_custom_policies_integration.py::test_pre_scan_with_cloned_checks``).
    _VERIFICATION_DIR = os.path.dirname(__file__)

    def pytest_collection_modifyitems(items):
        forked_mark = pytest.mark.forked
        for item in items:
            try:
                item_path = str(item.fspath)
            except Exception:
                continue
            if item_path.startswith(_VERIFICATION_DIR):
                item.add_marker(forked_mark)
# ──────────────────────────────────────────────────────────────────────────────


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
