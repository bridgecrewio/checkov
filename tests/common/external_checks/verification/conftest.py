"""Fixtures for external-checks verification tests.

Keypairs are generated in-memory at session scope so no PEM files are
committed to the repo. On-disk fixture trees are built into pytest's
per-test ``tmp_path``.

Every signed file ends with a trailer line of the form
``# checkov-digest: <lowercase-hex-DER-signature>\\n``. The
:func:`_append_trailer` helper produces it; fixtures call into it
instead of writing sidecar files.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Callable

import pytest
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, ed25519, rsa


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


def _append_trailer(body: bytes, priv: ec.EllipticCurvePrivateKey) -> bytes:
    """Return ``body + b"# checkov-digest: <hex>\\n"`` ready to write to disk."""
    sig_der = _sign_p256(priv, body)
    return body + b"# checkov-digest: " + sig_der.hex().encode("ascii") + b"\n"


@pytest.fixture(scope="session")
def keypair_a() -> tuple[bytes, ec.EllipticCurvePrivateKey]:
    return _gen_p256_pem()


@pytest.fixture(scope="session")
def keypair_b() -> tuple[bytes, ec.EllipticCurvePrivateKey]:
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


# Keys the verifier must reject: anything that isn't secp256r1 ECDSA.

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


@pytest.fixture
def make_sign() -> Callable[[ec.EllipticCurvePrivateKey, bytes], bytes]:
    """Return a callable that produces a DER signature over given bytes."""
    return _sign_p256


@pytest.fixture
def make_trailer() -> Callable[[bytes, ec.EllipticCurvePrivateKey], bytes]:
    """Return a callable that returns ``body + trailer-line`` for any body+key."""
    return _append_trailer


# Canonical pre-trailer bodies for ``valid_dir`` — module-level so tests
# can compare the verifier's returned bytes against the originals without
# re-deriving them from the on-disk file. An empty ``__init__.py`` is
# signed as a comment-only file; its body before the trailer is b"".
_VALID_BODIES: "dict[str, bytes]" = {
    "__init__.py": b"",
    "aws_check.py": b"# valid check\nCHECK_ID = 'CKV_T_1'\n",
    "_helper.py": (
        b"# helper module\n"
        b"HELPER = True\n"
        + b"# padding line\n" * 200  # nontrivial size so truncation bugs surface
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
    """One file in the valid dir has had a stray line appended after the trailer.

    Violates the "exactly one trailing newline" rule and is the customer-
    equivalent of an end-of-file-fixer hook adding a blank line.
    """
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
