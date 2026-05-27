"""Tests for the process-global verified-sources registry."""
from __future__ import annotations

import os
from pathlib import Path

import pytest

from checkov.common.external_checks.verification import SignatureVerificationError
from checkov.common.external_checks.verification.sources_registry import (
    get_verified_sources_for_directory,
    is_verification_active,
    reset_for_tests,
    verify_and_register,
)


@pytest.fixture(autouse=True)
def _reset_registry():
    """Clear the process-global registry around every test."""
    reset_for_tests()
    try:
        yield
    finally:
        reset_for_tests()


def test_inactive_when_no_keys_configured():
    """Empty key list = no-op; registry stays inactive (backward compat)."""
    verify_and_register(["/some/dir"], [])
    assert is_verification_active() is False
    assert get_verified_sources_for_directory("/some/dir") is None


def test_active_after_successful_verification(
    valid_dir: Path, key_a_pub_pem: bytes, tmp_path: Path,
):
    """A successful verify_and_register flips is_verification_active to True."""
    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    verify_and_register([str(valid_dir)], [str(key_path)])
    assert is_verification_active() is True


def test_lookup_returns_subset_for_directory(
    valid_dir: Path, key_a_pub_pem: bytes, tmp_path: Path,
):
    """get_verified_sources_for_directory returns only this dir's files."""
    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    verify_and_register([str(valid_dir)], [str(key_path)])

    sources = get_verified_sources_for_directory(str(valid_dir))
    assert sources is not None
    names = sorted(os.path.basename(p) for p in sources)
    assert names == ["__init__.py", "_helper.py", "aws_check.py"]


def test_lookup_for_unrelated_directory_returns_empty_dict(
    valid_dir: Path, key_a_pub_pem: bytes, tmp_path: Path,
):
    """A directory outside the verified set gets an empty allowlist, not None.

    Empty allowlist + active verification = loader refuses every .py
    file under that directory. Returning ``None`` here would be wrong
    — it would mean "verification disabled" and the loader would
    silently fall back to disk loads.
    """
    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    verify_and_register([str(valid_dir)], [str(key_path)])

    other = tmp_path / "elsewhere"
    other.mkdir()
    sources = get_verified_sources_for_directory(str(other))
    assert sources == {}


def test_verification_failure_propagates(
    unsigned_dir: Path, key_a_pub_pem: bytes, tmp_path: Path,
):
    """A bad dir raises SignatureVerificationError; registry stays inactive."""
    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)

    with pytest.raises(SignatureVerificationError):
        verify_and_register([str(unsigned_dir)], [str(key_path)])

    # Failed verification must NOT leave a half-populated registry.
    assert is_verification_active() is False


def test_reset_for_tests_clears_state(
    valid_dir: Path, key_a_pub_pem: bytes, tmp_path: Path,
):
    """reset_for_tests undoes the registration."""
    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    verify_and_register([str(valid_dir)], [str(key_path)])
    assert is_verification_active() is True

    reset_for_tests()
    assert is_verification_active() is False
    assert get_verified_sources_for_directory(str(valid_dir)) is None
