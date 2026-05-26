"""Behavioural tests for the external-checks verification library.

OPSEC: every test name, assertion string, and parametrize ID in this file
is outcome-focused. Tests do **not** name attack mechanics; they assert
that valid input is accepted and invalid input is rejected.

Cross-references to the design plan (which lives in an internal repo) are
deliberately omitted from this file so the public test surface reads as
contract validation rather than an enumeration of defended attacks.
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest

from checkov.common.external_checks.verification import (
    SignatureVerificationError,
    VerificationResult,
    load_public_keys,
    verify_external_checks_dirs,
    verify_file,
)


# --- Library happy path ----------------------------------------------------

def test_accepts_valid_input(valid_dir: Path, key_a_pub_pem: bytes, tmp_path: Path):
    """A signed directory verifies and returns the source bytes of every file."""
    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])

    verified = verify_external_checks_dirs([str(valid_dir)], keys)

    # Every Python-loadable file under the dir must be present in the map.
    assert sorted(os.path.basename(p) for p in verified) == sorted(
        ["__init__.py", "_helper.py", "aws_check.py"]
    )
    # The bytes returned are the bytes the loader will execute.
    aws_path = str(valid_dir / "aws_check.py")
    assert verified[aws_path] == (valid_dir / "aws_check.py").read_bytes()


def test_accepts_with_any_configured_key(
    valid_dir: Path, key_a_pub_pem: bytes, key_b_pub_pem: bytes, tmp_path: Path
):
    """Rotation: a file signed by key A passes when verifier is configured
    with ``[B, A]``."""
    key_a = tmp_path / "key_a.pem"
    key_a.write_bytes(key_a_pub_pem)
    key_b = tmp_path / "key_b.pem"
    key_b.write_bytes(key_b_pub_pem)

    # Configure B first, then A. valid_dir was signed by A.
    keys = load_public_keys([str(key_b), str(key_a)])
    verified = verify_external_checks_dirs([str(valid_dir)], keys)
    assert len(verified) == 3


# --- Library rejection paths ----------------------------------------------

def test_rejects_invalid_input(tampered_dir: Path, key_a_pub_pem: bytes, tmp_path: Path):
    """Bytes changed after signing → directory is rejected."""
    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])

    with pytest.raises(SignatureVerificationError) as exc:
        verify_external_checks_dirs([str(tampered_dir)], keys)

    assert "signature verification failed" in str(exc.value).lower()


def test_rejects_missing_signature(unsigned_dir: Path, key_a_pub_pem: bytes, tmp_path: Path):
    """No ``.sig`` sidecar present → directory is rejected."""
    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])

    with pytest.raises(SignatureVerificationError) as exc:
        verify_external_checks_dirs([str(unsigned_dir)], keys)

    assert "missing signature" in str(exc.value).lower()


def test_rejects_unknown_key(valid_dir: Path, key_b_pub_pem: bytes, tmp_path: Path):
    """Signed by a key not in the configured trust list → rejected."""
    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_b_pub_pem)  # B configured, but dir signed by A
    keys = load_public_keys([str(key_path)])

    with pytest.raises(SignatureVerificationError):
        verify_external_checks_dirs([str(valid_dir)], keys)


def test_rejects_directory_with_partial_signing(
    partial_dir: Path, key_a_pub_pem: bytes, tmp_path: Path
):
    """Whole directory is rejected if any importable Python file lacks a signature."""
    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])

    with pytest.raises(SignatureVerificationError) as exc:
        verify_external_checks_dirs([str(partial_dir)], keys)

    # The unsigned ``__init__.py`` must be named in the error so the customer
    # can locate it.
    assert "__init__.py" in str(exc.value)


def test_skips_non_python_files(mixed_dir: Path, key_a_pub_pem: bytes, tmp_path: Path):
    """Non-Python files (YAML / JSON / Markdown / LICENSE) are ignored.

    Pins the v1 scope contract: the verifier only handles Python-loadable
    files. If YAML signing is ever enabled, this test must be updated and
    that update is the design-discussion tripwire.
    """
    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])

    verified = verify_external_checks_dirs([str(mixed_dir)], keys)
    # Non-Python files are not in the verified map.
    assert not any(p.endswith((".yaml", ".md", "LICENSE")) for p in verified)
    # But Python files still are.
    assert any(p.endswith("aws_check.py") for p in verified)


def test_is_noop_without_configured_keys(valid_dir: Path):
    """Calling the verifier with no keys is a no-op (backward compatibility)."""
    verified = verify_external_checks_dirs([str(valid_dir)], [])
    assert verified == {}


def test_reports_offending_path_on_failure(
    valid_dir: Path, key_a_pub_pem: bytes, tmp_path: Path
):
    """A single bad file in a directory of many produces an error that names
    the offending relative path, for customer debugging."""
    # Tamper exactly one file
    (valid_dir / "_helper.py").write_bytes(b"# tampered\nHELPER = 'evil'\n")

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])

    with pytest.raises(SignatureVerificationError) as exc:
        verify_external_checks_dirs([str(valid_dir)], keys)
    assert "_helper.py" in str(exc.value)


# --- Key-format rejection (parametrised; IDs are opaque) ------------------

@pytest.mark.parametrize("format_id", ["format_a", "format_b", "format_c"])
def test_rejects_unsupported_key_format(
    format_id: str,
    unsupported_key_format_a: bytes,
    unsupported_key_format_b: bytes,
    unsupported_key_format_c: bytes,
    tmp_path: Path,
):
    """Public keys that aren't the supported format are rejected up-front."""
    pem_by_id = {
        "format_a": unsupported_key_format_a,
        "format_b": unsupported_key_format_b,
        "format_c": unsupported_key_format_c,
    }
    key_path = tmp_path / "key.pem"
    key_path.write_bytes(pem_by_id[format_id])

    with pytest.raises(SignatureVerificationError) as exc:
        load_public_keys([str(key_path)])

    assert "unsupported key format" in str(exc.value).lower()


# --- Malformed signature payload -----------------------------------------

def test_rejects_malformed_signature(valid_dir: Path, key_a_pub_pem: bytes, tmp_path: Path):
    """A sidecar whose bytes don't decode to a valid signature is rejected."""
    sig_path = valid_dir / "aws_check.py.sig"
    sig_path.write_bytes(b"\x00\x01\x02not a valid signature")

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])

    with pytest.raises(SignatureVerificationError):
        verify_external_checks_dirs([str(valid_dir)], keys)


# --- Path-escape rejection -----------------------------------------------

def test_rejects_path_escape_via_link(
    link_escape_dir: Path, key_a_pub_pem: bytes, tmp_path: Path
):
    """A path construct that resolves outside the verified directory is rejected."""
    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])

    with pytest.raises(SignatureVerificationError):
        verify_external_checks_dirs([str(link_escape_dir)], keys)


# --- Single-file verifier surface ----------------------------------------
# ``verify_file`` is the lower-level primitive that ``verify_external_checks_dirs``
# composes. The enum return values are part of the public API.

def test_verify_file_returns_ok_for_valid_input(
    valid_dir: Path, key_a_pub_pem: bytes, tmp_path: Path
):
    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])

    result = verify_file(
        str(valid_dir / "aws_check.py"),
        str(valid_dir / "aws_check.py.sig"),
        keys,
    )
    assert result == VerificationResult.OK


def test_verify_file_returns_no_signature_when_sidecar_absent(
    unsigned_dir: Path, key_a_pub_pem: bytes, tmp_path: Path
):
    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])

    result = verify_file(
        str(unsigned_dir / "aws_check.py"),
        str(unsigned_dir / "aws_check.py.sig"),
        keys,
    )
    assert result == VerificationResult.NO_SIGNATURE


def test_verify_file_returns_bad_signature_when_bytes_changed(
    tampered_dir: Path, key_a_pub_pem: bytes, tmp_path: Path
):
    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])

    result = verify_file(
        str(tampered_dir / "aws_check.py"),
        str(tampered_dir / "aws_check.py.sig"),
        keys,
    )
    assert result in (VerificationResult.BAD_SIGNATURE, VerificationResult.UNKNOWN_KEY)
