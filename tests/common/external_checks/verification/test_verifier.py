"""Behavioural tests for the external-checks verification library."""
from __future__ import annotations

import os
from pathlib import Path

import pytest

from checkov.common.external_checks.verification import (
    FileVerification,
    SignatureVerificationError,
    VerificationResult,
    load_public_keys,
    verify_bytes,
    verify_external_checks_dirs,
    verify_file,
    verify_file_with_bytes,
)


# --- Library happy path ----------------------------------------------------

def test_accepts_valid_input(valid_dir: Path, key_a_pub_pem: bytes, tmp_path: Path):
    """A signed directory verifies and returns the exact source bytes of every file."""
    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])

    verified = verify_external_checks_dirs([str(valid_dir)], keys)

    assert sorted(os.path.basename(p) for p in verified) == sorted(
        ["__init__.py", "_helper.py", "aws_check.py"]
    )
    # Byte-identity for every verified file, not just one.
    for path, returned_bytes in verified.items():
        on_disk = Path(path).read_bytes()
        assert returned_bytes == on_disk, f"byte mismatch for {path}"
    # And one of them is nontrivial (helper has padding) so a truncation
    # bug at any I/O boundary would surface.
    helper_bytes = verified[str(valid_dir / "_helper.py")]
    assert len(helper_bytes) > 1024


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

    The verifier covers only Python-loadable files (``LOADABLE_SUFFIXES``).
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


# --- Key-format rejection (parametrised) ----------------------------------

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


def test_verify_file_returns_unknown_key_when_bytes_changed(
    tampered_dir: Path, key_a_pub_pem: bytes, tmp_path: Path
):
    """Mutating payload bytes after signing makes the signature valid for no
    configured key — that is ``UNKNOWN_KEY``, not ``BAD_SIGNATURE`` (the
    signature itself is still a well-formed DER ECDSA pair).
    """
    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])

    result = verify_file(
        str(tampered_dir / "aws_check.py"),
        str(tampered_dir / "aws_check.py.sig"),
        keys,
    )
    assert result == VerificationResult.UNKNOWN_KEY


# --- F1: nonexistent and empty-string dir entries ------------------------

def test_rejects_nonexistent_dir(key_a_pub_pem: bytes, tmp_path: Path):
    """A typo'd directory path must raise, not silently return an empty map."""
    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])

    with pytest.raises(SignatureVerificationError) as exc:
        verify_external_checks_dirs([str(tmp_path / "does-not-exist")], keys)
    assert "does not exist" in str(exc.value)


def test_empty_string_dir_entries_are_ignored(
    valid_dir: Path, key_a_pub_pem: bytes, tmp_path: Path
):
    """Empty-string entries in dirs[] are silently skipped (CLI artefact)."""
    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])
    verified = verify_external_checks_dirs(["", str(valid_dir), ""], keys)
    assert len(verified) == 3


# --- F2: IO_ERROR & verify_file_with_bytes invariants --------------------

def test_verify_file_with_bytes_returns_empty_payload_on_failure(
    tampered_dir: Path, key_a_pub_pem: bytes, tmp_path: Path
):
    """payload_bytes must be b'' on any non-OK result."""
    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])

    result = verify_file_with_bytes(
        str(tampered_dir / "aws_check.py"),
        str(tampered_dir / "aws_check.py.sig"),
        keys,
    )
    assert isinstance(result, FileVerification)
    assert result.result != VerificationResult.OK
    assert result.payload_bytes == b""


def test_verify_file_returns_io_error_when_payload_unreadable(
    valid_dir: Path, key_a_pub_pem: bytes, tmp_path: Path
):
    """Sidecar present, payload deleted between sig-check and payload-read."""
    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])

    payload = valid_dir / "aws_check.py"
    sig = valid_dir / "aws_check.py.sig"
    payload.unlink()  # sig still there, payload gone

    result = verify_file(str(payload), str(sig), keys)
    assert result == VerificationResult.IO_ERROR


# --- F3: oversized signature sidecar -------------------------------------

def test_rejects_oversized_signature(
    valid_dir: Path, key_a_pub_pem: bytes, tmp_path: Path
):
    """A sidecar larger than the size cap is rejected as BAD_SIGNATURE."""
    sig_path = valid_dir / "aws_check.py.sig"
    sig_path.write_bytes(b"\x00" * 2048)  # 2 KiB > cap

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])

    with pytest.raises(SignatureVerificationError) as exc:
        verify_external_checks_dirs([str(valid_dir)], keys)
    assert "signature verification failed" in str(exc.value).lower()


# --- F4: path-escape and other failures coexist --------------------------

def test_path_escape_does_not_mask_other_failures_in_same_dir(
    tmp_path: Path, priv_a, key_a_pub_pem: bytes
):
    """A symlink-escape and a missing-sig in the same dir must both be reported."""
    root = tmp_path / "mixed"
    root.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "evil.py").write_bytes(b"# outside")
    try:
        os.symlink(outside / "evil.py", root / "linked.py")
    except (OSError, NotImplementedError):
        pytest.skip("symlinks unsupported on this platform")
    (root / "unsigned.py").write_bytes(b"# no sig\n")

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])

    with pytest.raises(SignatureVerificationError) as exc:
        verify_external_checks_dirs([str(root)], keys)
    msg = str(exc.value)
    assert "linked.py" in msg
    assert "unsigned.py" in msg


# --- F5: duplicate / nested dirs -----------------------------------------

def test_rejects_duplicate_dirs(
    valid_dir: Path, key_a_pub_pem: bytes, tmp_path: Path
):
    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])
    with pytest.raises(SignatureVerificationError) as exc:
        verify_external_checks_dirs([str(valid_dir), str(valid_dir)], keys)
    assert "duplicate" in str(exc.value).lower()


def test_rejects_nested_dirs(
    valid_dir: Path, key_a_pub_pem: bytes, tmp_path: Path
):
    """A parent dir and one of its children cannot both be configured."""
    parent = valid_dir.parent
    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])
    with pytest.raises(SignatureVerificationError) as exc:
        verify_external_checks_dirs([str(parent), str(valid_dir)], keys)
    assert "overlap" in str(exc.value).lower()


# --- F5a: dup/overlap errors coexist with other failures -----------------

def test_duplicate_and_nonexistent_dirs_are_both_reported(
    valid_dir: Path, key_a_pub_pem: bytes, tmp_path: Path
):
    """A typo'd dir and a duplicate dir in the same call must both surface
    in the failure list so the customer fixes everything in one CI cycle.
    """
    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])

    typo = str(tmp_path / "does-not-exist")
    with pytest.raises(SignatureVerificationError) as exc:
        verify_external_checks_dirs(
            [str(valid_dir), str(valid_dir), typo], keys
        )
    msg = str(exc.value)
    assert "duplicate" in msg.lower(), "duplicate dir not reported"
    assert "does not exist" in msg, "typo'd dir not reported"


def test_duplicate_dir_does_not_skip_other_dirs(
    valid_dir: Path, key_a_pub_pem: bytes, tmp_path: Path, priv_a, make_sign
):
    """When dirs=[A, A, B] and B has a missing-sig file, B's failure must
    still be reported alongside the duplicate-A error."""
    second = tmp_path / "second"
    second.mkdir()
    (second / "unsigned.py").write_bytes(b"# no sig\n")

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])

    with pytest.raises(SignatureVerificationError) as exc:
        verify_external_checks_dirs(
            [str(valid_dir), str(valid_dir), str(second)], keys
        )
    msg = str(exc.value)
    assert "duplicate" in msg.lower()
    assert "unsigned.py" in msg


# --- F6: verify_bytes empty-key guard ------------------------------------

def test_verify_bytes_rejects_empty_key_list():
    with pytest.raises(ValueError):
        verify_bytes(b"payload", b"\x30\x06\x02\x01\x01\x02\x01\x01", [])


# --- F7: sibling-prefix and broken-symlink path-escape -------------------

def test_sibling_prefix_collision_is_not_an_escape(
    tmp_path: Path, priv_a, key_a_pub_pem: bytes, make_sign
):
    """/x/checks-evil/foo.py must not be considered inside /x/checks."""
    checks = tmp_path / "checks"
    checks.mkdir()
    body = b"# inside\n"
    (checks / "foo.py").write_bytes(body)
    (checks / "foo.py.sig").write_bytes(make_sign(priv_a, body))

    # checks-evil is a sibling of checks. Its files must not poison checks/.
    checks_evil = tmp_path / "checks-evil"
    checks_evil.mkdir()
    (checks_evil / "bad.py").write_bytes(b"# outside\n")

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])

    # Only checks/ is configured; checks-evil/ must not be reached.
    verified = verify_external_checks_dirs([str(checks)], keys)
    assert set(verified) == {str(checks / "foo.py")}


def test_dangling_symlink_is_rejected(
    tmp_path: Path, key_a_pub_pem: bytes
):
    """A .py symlink whose target does not exist is rejected."""
    root = tmp_path / "dangling"
    root.mkdir()
    try:
        os.symlink(tmp_path / "no-such-target", root / "broken.py")
    except (OSError, NotImplementedError):
        pytest.skip("symlinks unsupported on this platform")

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])
    with pytest.raises(SignatureVerificationError) as exc:
        verify_external_checks_dirs([str(root)], keys)
    assert "broken.py" in str(exc.value)


# --- F13: every loadable extension --------------------------------------

def test_accepts_every_loadable_extension(
    multi_extension_dir: Path, key_a_pub_pem: bytes, tmp_path: Path
):
    """The verifier covers .py, .pyc, .pyi, .so, .pyd uniformly."""
    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])

    verified = verify_external_checks_dirs([str(multi_extension_dir)], keys)
    names = sorted(os.path.basename(p) for p in verified)
    assert names == sorted([
        "__init__.py", "check.py", "compiled.pyc",
        "typings.pyi", "native.so", "windows.pyd",
    ])
