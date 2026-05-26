"""Fixtures for external-checks verification tests.

Keypairs are generated in-memory at session scope so no PEM files are
committed to the repo. On-disk fixture trees are built into pytest's
per-test ``tmp_path``.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Callable

import pytest
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa, ed25519


# --- Key generation --------------------------------------------------------

def _gen_p256_pem() -> tuple[bytes, ec.EllipticCurvePrivateKey]:
    """Return ``(public_key_pem_bytes, private_key_object)`` for a fresh P-256 key."""
    priv = ec.generate_private_key(ec.SECP256R1())
    pub_pem = priv.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return pub_pem, priv


def _sign_p256(priv: ec.EllipticCurvePrivateKey, payload: bytes) -> bytes:
    """Produce a DER ECDSA-SHA256 signature over ``payload``."""
    return priv.sign(payload, ec.ECDSA(hashes.SHA256()))


# --- Session-scoped keypairs ----------------------------------------------

@pytest.fixture(scope="session")
def keypair_a() -> tuple[bytes, ec.EllipticCurvePrivateKey]:
    """Primary P-256 keypair: returns ``(public_pem, private_key_object)``."""
    return _gen_p256_pem()


@pytest.fixture(scope="session")
def keypair_b() -> tuple[bytes, ec.EllipticCurvePrivateKey]:
    """Secondary P-256 keypair for rotation / multi-key tests."""
    return _gen_p256_pem()


@pytest.fixture(scope="session")
def key_a_pub_pem(keypair_a) -> bytes:
    return keypair_a[0]


@pytest.fixture(scope="session")
def key_b_pub_pem(keypair_b) -> bytes:
    return keypair_b[0]


@pytest.fixture(scope="session")
def priv_a(keypair_a) -> ec.EllipticCurvePrivateKey:
    return keypair_a[1]


@pytest.fixture(scope="session")
def priv_b(keypair_b) -> ec.EllipticCurvePrivateKey:
    return keypair_b[1]


# --- Unsupported key fixtures ---------------------------------------------
# The verifier rejects any key that isn't exactly secp256r1 ECDSA.

def _rsa_pub_pem() -> bytes:
    priv = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return priv.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )


def _ed25519_pub_pem() -> bytes:
    priv = ed25519.Ed25519PrivateKey.generate()
    return priv.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )


def _p384_pub_pem() -> bytes:
    priv = ec.generate_private_key(ec.SECP384R1())
    return priv.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )


@pytest.fixture(scope="session")
def unsupported_key_format_a() -> bytes:
    return _rsa_pub_pem()


@pytest.fixture(scope="session")
def unsupported_key_format_b() -> bytes:
    return _ed25519_pub_pem()


@pytest.fixture(scope="session")
def unsupported_key_format_c() -> bytes:
    return _p384_pub_pem()


# --- Directory builders ----------------------------------------------------
# Each builder writes a fresh tree to ``tmp_path`` and returns the path.
# This keeps fixtures byte-stable across runs while letting tests freely
# mutate the tree.

@pytest.fixture
def make_sign() -> Callable[[ec.EllipticCurvePrivateKey, bytes], bytes]:
    """Return a callable that produces a DER signature over given bytes."""
    return _sign_p256


@pytest.fixture
def valid_dir(tmp_path: Path, priv_a) -> Path:
    """Directory with every Python-loadable file properly signed.

    Mirrors the §5.1 fixture-tree layout (``__init__.py``, a top-level check,
    a helper module). Each ``.py`` has an adjacent ``.py.sig`` carrying the
    raw DER ECDSA-P256 signature of the file's bytes.
    """
    root = tmp_path / "valid"
    root.mkdir()
    files = {
        "__init__.py": b"",
        "aws_check.py": b"# valid check\nCHECK_ID = 'CKV_T_1'\n",
        "_helper.py": (
            b"# helper module\n"
            b"HELPER = True\n"
            + b"# padding line\n" * 200  # nontrivial size so truncation bugs surface
        ),
    }
    for name, body in files.items():
        f = root / name
        f.write_bytes(body)
        sig = _sign_p256(priv_a, body)
        (root / f"{name}.sig").write_bytes(sig)
    return root


@pytest.fixture
def tampered_dir(valid_dir: Path) -> Path:
    """Directory where one file's bytes were mutated after signing."""
    target = valid_dir / "aws_check.py"
    body = target.read_bytes()
    target.write_bytes(body + b"# mutated\n")
    return valid_dir


@pytest.fixture
def unsigned_dir(tmp_path: Path) -> Path:
    """Directory with Python files but no ``.sig`` sidecars at all."""
    root = tmp_path / "unsigned"
    root.mkdir()
    (root / "__init__.py").write_bytes(b"")
    (root / "aws_check.py").write_bytes(b"# unsigned\nCHECK_ID = 'CKV_T_1'\n")
    return root


@pytest.fixture
def partial_dir(tmp_path: Path, priv_a) -> Path:
    """Directory where some Python files are signed and others are not."""
    root = tmp_path / "partial"
    root.mkdir()
    # Signed file
    signed_name = "aws_check.py"
    signed_body = b"# signed\nCHECK_ID = 'CKV_T_1'\n"
    (root / signed_name).write_bytes(signed_body)
    (root / f"{signed_name}.sig").write_bytes(_sign_p256(priv_a, signed_body))
    # Unsigned __init__.py (a real loader path: package init runs at import)
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
    """Valid signed dir plus a non-Python file that the verifier should ignore."""
    (valid_dir / "README.md").write_bytes(b"# Docs\n")
    (valid_dir / "checks.yaml").write_bytes(b"id: CKV_T_4\n")
    (valid_dir / "LICENSE").write_bytes(b"Apache 2.0\n")
    return valid_dir


@pytest.fixture
def link_escape_dir(tmp_path: Path, priv_a) -> Path:
    """Directory containing a path-like construct that resolves outside the tree.

    Skipped on platforms where the construct cannot be created (e.g. some
    Windows configurations); the test that consumes this fixture will skip
    in that case.
    """
    outside = tmp_path / "outside"
    outside.mkdir()
    payload = outside / "evil.py"
    payload.write_bytes(b"# code outside the verified tree\n")

    root = tmp_path / "with_link"
    root.mkdir()
    (root / "__init__.py").write_bytes(b"")
    body = b"# inside check\n"
    inside = root / "inside.py"
    inside.write_bytes(body)
    (root / "inside.py.sig").write_bytes(_sign_p256(priv_a, body))

    link = root / "innocent.py"
    try:
        os.symlink(payload, link)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks not supported on this platform")
    return root


@pytest.fixture
def multi_extension_dir(tmp_path: Path, priv_a) -> Path:
    """Directory exercising every entry of LOADABLE_SUFFIXES.

    Bytes of .so/.pyc/.pyd are not valid ELF/bytecode — that does not
    matter to the verifier, which treats every file as opaque bytes.
    """
    root = tmp_path / "multi"
    root.mkdir()
    files = {
        "__init__.py": b"",
        "check.py": b"# py source\n",
        "compiled.pyc": b"\x55\x0d\x0d\x0a" + b"\x00" * 12 + b"# fake pyc\n",
        "typings.pyi": b"def foo() -> int: ...\n",
        "native.so": b"\x7fELF" + b"\x00" * 32,
        "windows.pyd": b"MZ" + b"\x00" * 30,
    }
    for name, body in files.items():
        (root / name).write_bytes(body)
        (root / f"{name}.sig").write_bytes(_sign_p256(priv_a, body))
    return root
