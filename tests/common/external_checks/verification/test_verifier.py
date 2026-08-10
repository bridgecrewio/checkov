"""Behavioural tests for the external-checks verification library."""
from __future__ import annotations

import os
from pathlib import Path

import pytest

from checkov.common.external_checks.verification import (
    SignatureVerificationError,
    VerificationResult,
    load_public_keys,
    verify_bytes,
    verify_external_checks_dirs,
    verify_file,
)


def test_accepts_valid_input(
    valid_dir: Path, valid_bodies: "dict[str, bytes]",
    key_a_pub_pem: bytes, tmp_path: Path,
):
    """A signed directory verifies and returns the trailer-stripped bytes."""
    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])

    verified = verify_external_checks_dirs([str(valid_dir)], keys)

    assert sorted(os.path.basename(p) for p in verified) == sorted(
        ["__init__.py", "_helper.py", "aws_check.py"]
    )
    # Returned bytes are the trailer-stripped bodies (what the loader
    # will exec), not the bytes on disk (which include the trailer line).
    for path, returned_bytes in verified.items():
        name = os.path.basename(path)
        assert returned_bytes == valid_bodies[name], f"byte mismatch for {name}"

    helper_bytes = verified[str(valid_dir / "_helper.py")]
    assert len(helper_bytes) > 1024  # nontrivial size catches truncation bugs


def test_accepts_with_any_configured_key(
    valid_dir: Path, key_a_pub_pem: bytes, key_b_pub_pem: bytes, tmp_path: Path,
):
    """Rotation: file signed by key A passes when verifier has [B, A] configured."""
    key_a = tmp_path / "key_a.pem"
    key_a.write_bytes(key_a_pub_pem)
    key_b = tmp_path / "key_b.pem"
    key_b.write_bytes(key_b_pub_pem)

    keys = load_public_keys([str(key_b), str(key_a)])
    verified = verify_external_checks_dirs([str(valid_dir)], keys)
    assert len(verified) == 3


def test_rejects_invalid_input(
    mutated_dir: Path, key_a_pub_pem: bytes, tmp_path: Path,
):
    """Bytes appended after the trailer → directory is rejected.

    Either ``signature verification failed`` (BAD_SIG/UNKNOWN_KEY) or
    ``missing signature`` (NO_SIG) is acceptable — both are structurally
    correct refusals of a file with extra bytes after the trailer's
    newline.
    """
    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])

    with pytest.raises(SignatureVerificationError) as exc:
        verify_external_checks_dirs([str(mutated_dir)], keys)

    msg = str(exc.value).lower()
    assert "signature verification failed" in msg or "missing signature" in msg


def test_rejects_missing_signature(
    unsigned_dir: Path, key_a_pub_pem: bytes, tmp_path: Path,
):
    """No trailer line → ``missing signature``."""
    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])

    with pytest.raises(SignatureVerificationError) as exc:
        verify_external_checks_dirs([str(unsigned_dir)], keys)

    assert "missing signature" in str(exc.value).lower()


def test_rejects_unknown_key(
    valid_dir: Path, key_b_pub_pem: bytes, tmp_path: Path,
):
    """Signed by a key not in the trust list → rejected."""
    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_b_pub_pem)  # B configured, dir signed by A
    keys = load_public_keys([str(key_path)])

    with pytest.raises(SignatureVerificationError):
        verify_external_checks_dirs([str(valid_dir)], keys)


def test_rejects_directory_with_partial_signing(
    partial_dir: Path, key_a_pub_pem: bytes, tmp_path: Path,
):
    """Whole directory is rejected if any Python file lacks a trailer."""
    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])

    with pytest.raises(SignatureVerificationError) as exc:
        verify_external_checks_dirs([str(partial_dir)], keys)

    assert "__init__.py" in str(exc.value)


def test_ignores_non_python_text_files(
    mixed_dir: Path, key_a_pub_pem: bytes, tmp_path: Path,
):
    """Non-Python text files (YAML / Markdown / LICENSE) are silently passed.

    Binary loadable files are different — they are hard-rejected (see
    ``test_rejects_dir_containing_binary_loadable_file``).
    """
    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])

    verified = verify_external_checks_dirs([str(mixed_dir)], keys)
    assert not any(p.endswith((".yaml", ".md", "LICENSE")) for p in verified)
    assert any(p.endswith("aws_check.py") for p in verified)


def test_is_noop_without_configured_keys(valid_dir: Path):
    """Calling the verifier with no keys is a no-op."""
    verified = verify_external_checks_dirs([str(valid_dir)], [])
    assert verified == {}


def test_reports_offending_path_on_failure(
    valid_dir: Path, key_a_pub_pem: bytes, tmp_path: Path,
):
    """A single bad file in a directory of many produces an error that names it."""
    (valid_dir / "_helper.py").write_bytes(b"# modified\nHELPER = 'changed'\n")

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])

    with pytest.raises(SignatureVerificationError) as exc:
        verify_external_checks_dirs([str(valid_dir)], keys)
    assert "_helper.py" in str(exc.value)


@pytest.mark.parametrize("format_id", ["format_a", "format_b", "format_c", "format_d", "format_e"])
def test_rejects_unsupported_key_format(
    format_id: str,
    unsupported_key_format_a: bytes,
    unsupported_key_format_b: bytes,
    unsupported_key_format_c: bytes,
    unsupported_key_format_d: bytes,
    unsupported_key_format_e: bytes,
    tmp_path: Path,
):
    """Public keys that aren't P-256 ECDSA are rejected up-front.

    Covers RSA (format_a), Ed25519 (format_b), P-384 (format_c),
    SECP256K1 (format_d — the Bitcoin curve, which operators are most
    likely to accidentally use because it shows up in countless ECDSA
    tutorials and Stack Overflow answers), and P-521 (format_e — a NIST
    EC curve that looks superficially like P-256 but has a different
    key size).
    """
    pem_by_id = {
        "format_a": unsupported_key_format_a,
        "format_b": unsupported_key_format_b,
        "format_c": unsupported_key_format_c,
        "format_d": unsupported_key_format_d,
        "format_e": unsupported_key_format_e,
    }
    key_path = tmp_path / "key.pem"
    key_path.write_bytes(pem_by_id[format_id])

    with pytest.raises(SignatureVerificationError) as exc:
        load_public_keys([str(key_path)])

    assert "unsupported key format" in str(exc.value).lower()


def test_rejects_malformed_signature(
    valid_dir: Path, key_a_pub_pem: bytes, tmp_path: Path,
):
    """A trailer whose hex decodes to non-DER bytes is rejected.

    71 bytes of \\x00 satisfies the length range but fails strict-DER
    decode → BAD_SIGNATURE.
    """
    target = valid_dir / "aws_check.py"
    body = b"# valid check\nCHECK_ID = 'CKV_T_1'\n"
    bad_payload = (b"\x00" * 71).hex().encode("ascii")
    target.write_bytes(body + b"# checkov-digest: " + bad_payload + b"\n")

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])

    with pytest.raises(SignatureVerificationError) as exc:
        verify_external_checks_dirs([str(valid_dir)], keys)
    assert "signature verification failed" in str(exc.value).lower()


def test_rejects_path_escape_via_link(
    link_escape_dir: Path, key_a_pub_pem: bytes, tmp_path: Path,
):
    """A symlink that resolves outside the verified directory is rejected."""
    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])

    with pytest.raises(SignatureVerificationError):
        verify_external_checks_dirs([str(link_escape_dir)], keys)


def test_verify_file_returns_ok_for_valid_input(
    valid_dir: Path, valid_bodies: "dict[str, bytes]",
    key_a_pub_pem: bytes, tmp_path: Path,
):
    """``verify_file(path, keys)`` returns ``(OK, signed_bytes)`` for a signed file."""
    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])

    result, signed_bytes = verify_file(str(valid_dir / "aws_check.py"), keys)
    assert result == VerificationResult.OK
    assert signed_bytes == valid_bodies["aws_check.py"]


def test_verify_file_returns_no_signature_when_trailer_absent(
    unsigned_dir: Path, key_a_pub_pem: bytes, tmp_path: Path,
):
    """File without trailer line → ``(NO_SIGNATURE, b"")``."""
    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])

    result, signed_bytes = verify_file(str(unsigned_dir / "aws_check.py"), keys)
    assert result == VerificationResult.NO_SIGNATURE
    assert signed_bytes == b""


def test_verify_file_returns_unknown_key_when_bytes_changed(
    valid_dir: Path, key_a_pub_pem: bytes, tmp_path: Path,
):
    """Replacing the body but keeping the (now stale) trailer → UNKNOWN_KEY.

    The trailer is still a well-formed DER ECDSA pair; it just no longer
    verifies for the new body. UNKNOWN_KEY, not BAD_SIGNATURE.
    """
    target = valid_dir / "aws_check.py"
    original = target.read_bytes()
    body = original[:-1]  # strip terminating \n
    last_nl = body.rfind(b"\n")
    trailer_with_nl = original[last_nl + 1:]  # trailer line + \n
    target.write_bytes(b"# modified body\n" + trailer_with_nl)

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])

    result, signed_bytes = verify_file(str(target), keys)
    assert result == VerificationResult.UNKNOWN_KEY
    assert signed_bytes == b""


def test_verify_file_returns_io_error_when_file_unreadable(
    valid_dir: Path, key_a_pub_pem: bytes, tmp_path: Path,
):
    """File that cannot be read returns ``(IO_ERROR, b"")``.

    We open a directory path: ``open(directory, "rb")`` raises
    ``IsADirectoryError`` on POSIX, ``PermissionError`` on Windows —
    both ``OSError`` subclasses the verifier catches.
    """
    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])

    result, signed_bytes = verify_file(str(valid_dir), keys)
    assert result == VerificationResult.IO_ERROR
    assert signed_bytes == b""


def test_rejects_nonexistent_dir(key_a_pub_pem: bytes, tmp_path: Path):
    """A typo'd directory path raises, not silently returns an empty map."""
    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])

    with pytest.raises(SignatureVerificationError) as exc:
        verify_external_checks_dirs([str(tmp_path / "does-not-exist")], keys)
    assert "does not exist" in str(exc.value)


def test_empty_string_dir_entries_are_ignored(
    valid_dir: Path, key_a_pub_pem: bytes, tmp_path: Path,
):
    """Empty-string entries in dirs[] are silently skipped (CLI artefact)."""
    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])
    verified = verify_external_checks_dirs(["", str(valid_dir), ""], keys)
    assert len(verified) == 3


def test_path_escape_does_not_mask_other_failures_in_same_dir(
    tmp_path: Path, priv_a, key_a_pub_pem: bytes,
):
    """A symlink-escape and a missing-trailer in the same dir are both reported."""
    root = tmp_path / "mixed"
    root.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "outside_module.py").write_bytes(b"# outside")
    try:
        os.symlink(outside / "outside_module.py", root / "linked.py")
    except (OSError, NotImplementedError):
        pytest.skip("symlinks unsupported on this platform")
    (root / "unsigned.py").write_bytes(b"# no trailer\n")

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])

    with pytest.raises(SignatureVerificationError) as exc:
        verify_external_checks_dirs([str(root)], keys)
    msg = str(exc.value)
    assert "linked.py" in msg
    assert "unsigned.py" in msg


def test_rejects_duplicate_dirs(
    valid_dir: Path, key_a_pub_pem: bytes, tmp_path: Path,
):
    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])
    with pytest.raises(SignatureVerificationError) as exc:
        verify_external_checks_dirs([str(valid_dir), str(valid_dir)], keys)
    assert "duplicate" in str(exc.value).lower()


def test_rejects_nested_dirs(
    valid_dir: Path, key_a_pub_pem: bytes, tmp_path: Path,
):
    """A parent dir and one of its children cannot both be configured."""
    parent = valid_dir.parent
    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])
    with pytest.raises(SignatureVerificationError) as exc:
        verify_external_checks_dirs([str(parent), str(valid_dir)], keys)
    assert "overlap" in str(exc.value).lower()


def test_duplicate_and_nonexistent_dirs_are_both_reported(
    valid_dir: Path, key_a_pub_pem: bytes, tmp_path: Path,
):
    """A typo'd dir and a duplicate dir in the same call must both surface."""
    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])

    typo = str(tmp_path / "does-not-exist")
    with pytest.raises(SignatureVerificationError) as exc:
        verify_external_checks_dirs(
            [str(valid_dir), str(valid_dir), typo], keys,
        )
    msg = str(exc.value)
    assert "duplicate" in msg.lower(), "duplicate dir not reported"
    assert "does not exist" in msg, "typo'd dir not reported"


def test_duplicate_dir_does_not_skip_other_dirs(
    valid_dir: Path, key_a_pub_pem: bytes, tmp_path: Path,
):
    """When dirs=[A, A, B] and B has a missing-trailer file, B's failure must
    still be reported alongside the duplicate-A error."""
    second = tmp_path / "second"
    second.mkdir()
    (second / "unsigned.py").write_bytes(b"# no trailer\n")

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])

    with pytest.raises(SignatureVerificationError) as exc:
        verify_external_checks_dirs(
            [str(valid_dir), str(valid_dir), str(second)], keys,
        )
    msg = str(exc.value)
    assert "duplicate" in msg.lower()
    assert "unsigned.py" in msg


def test_verify_bytes_rejects_empty_key_list():
    """``verify_bytes`` requires at least one key; empty list raises ValueError."""
    with pytest.raises(ValueError):
        verify_bytes(b"# checkov-digest: 00\n", [])


def test_sibling_prefix_collision_is_not_an_escape(
    tmp_path: Path, priv_a, key_a_pub_pem: bytes, make_trailer,
):
    """``/x/checks-other/foo.py`` must not be considered inside ``/x/checks``."""
    checks = tmp_path / "checks"
    checks.mkdir()
    (checks / "foo.py").write_bytes(make_trailer(b"# inside\n", priv_a))

    checks_other = tmp_path / "checks-other"
    checks_other.mkdir()
    (checks_other / "bad.py").write_bytes(b"# outside\n")

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])

    verified = verify_external_checks_dirs([str(checks)], keys)
    assert set(verified) == {str(checks / "foo.py")}


def test_dangling_symlink_is_rejected(
    tmp_path: Path, key_a_pub_pem: bytes,
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


# Trailer-shape / wire-format rules.

def test_rejects_file_without_trailing_newline(
    valid_dir: Path, priv_a, key_a_pub_pem: bytes, tmp_path: Path,
):
    """A file that does not end with \\n cannot carry a trailer → NO_SIGNATURE."""
    target = valid_dir / "aws_check.py"
    body = target.read_bytes()
    assert body.endswith(b"\n")
    target.write_bytes(body.rstrip(b"\n"))

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])

    result, signed_bytes = verify_file(str(target), keys)
    assert result == VerificationResult.NO_SIGNATURE
    assert signed_bytes == b""


def test_rejects_file_with_double_trailing_newline(
    valid_dir: Path, priv_a, key_a_pub_pem: bytes, tmp_path: Path,
):
    """A file ending in \\n\\n — the "last line" is empty → NO_SIGNATURE.

    Most-likely IDE format-on-save failure (an end-of-file-fixer hook
    adding a second \\n).
    """
    target = valid_dir / "aws_check.py"
    target.write_bytes(target.read_bytes() + b"\n")

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])

    result, _ = verify_file(str(target), keys)
    assert result == VerificationResult.NO_SIGNATURE


def test_rejects_crlf_terminated_file(
    tmp_path: Path, priv_a, key_a_pub_pem: bytes, make_trailer,
):
    """A file with CRLF line endings → BAD_SIGNATURE.

    The last byte is \\n; the trailer's terminator was rewritten as
    \\r\\n. The trailer prefix slice still starts cleanly with
    ``# checkov-digest: ``, but the trailing \\r ends up inside the hex
    payload — \\r is not lowercase hex, so the payload guard rejects
    the trailer. The prefix-was-present check then maps the failure to
    BAD_SIGNATURE (corrupt trailer), not NO_SIGNATURE (no trailer at all).
    """
    body = b"def check():\r\n    return 'ok'\r\n"
    signed = make_trailer(body, priv_a)
    crlf_signed = signed[:-1] + b"\r\n"

    target = tmp_path / "check.py"
    target.write_bytes(crlf_signed)

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])

    result, _ = verify_file(str(target), keys)
    assert result == VerificationResult.BAD_SIGNATURE


def test_rejects_file_with_bom(
    valid_dir: Path, priv_a, key_a_pub_pem: bytes, tmp_path: Path,
):
    """A BOM prepended to a signed file → UNKNOWN_KEY.

    The signer signed bytes without a BOM. The verifier hashes the
    on-disk bytes including the BOM → mismatch. The trailer is
    structurally fine, so we land in UNKNOWN_KEY rather than
    NO_SIGNATURE / BAD_SIGNATURE.
    """
    target = valid_dir / "aws_check.py"
    target.write_bytes(b"\xef\xbb\xbf" + target.read_bytes())

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])

    result, _ = verify_file(str(target), keys)
    assert result == VerificationResult.UNKNOWN_KEY


@pytest.mark.parametrize(
    ("mutation_id", "trailer_replacement_bytes", "expected_result"),
    [
        # No space at all → the prefix ``# checkov-digest: `` does not
        # match → no trailer detected at all → NO_SIGNATURE.
        ("no_space_after_colon", b"# checkov-digest:", VerificationResult.NO_SIGNATURE),
        ("tab_after_colon", b"# checkov-digest:\t", VerificationResult.NO_SIGNATURE),
        # Extra space after the required one → prefix DOES match (prefix
        # is "# checkov-digest: ", and ":  " starts with ": "), but the
        # leading space ends up inside the hex payload and fails the
        # alphabet guard → BAD_SIGNATURE.
        ("two_spaces_after_colon", b"# checkov-digest:  ", VerificationResult.BAD_SIGNATURE),
        # Uppercase hex → prefix matches, payload fails the lowercase
        # alphabet guard → BAD_SIGNATURE.
        ("uppercase_hex_prefix", b"# checkov-digest: ", VerificationResult.BAD_SIGNATURE),
    ],
)
def test_rejects_trailer_with_wrong_whitespace_or_case(
    mutation_id: str,
    trailer_replacement_bytes: bytes,
    expected_result: VerificationResult,
    tmp_path: Path,
    priv_a,
    key_a_pub_pem: bytes,
    make_sign,
):
    """Trailer-shape mutations are rejected.

    Two-tier result mapping: if the prefix doesn't even match → the
    customer gets ``NO_SIGNATURE`` ("you forgot to sign"). If the prefix
    matches but the payload is structurally wrong → ``BAD_SIGNATURE``
    ("you signed it wrong"). Both diagnostics are useful to the customer
    in different ways.
    """
    body = b"def x():\n    pass\n"
    sig_der = make_sign(priv_a, body)
    hex_payload = sig_der.hex()
    if mutation_id == "uppercase_hex_prefix":
        hex_payload = hex_payload.upper()
    file_bytes = body + trailer_replacement_bytes + hex_payload.encode("ascii") + b"\n"

    target = tmp_path / "check.py"
    target.write_bytes(file_bytes)

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])

    result, _ = verify_file(str(target), keys)
    assert result == expected_result


def test_rejects_trailer_with_huge_hex_payload(
    tmp_path: Path, key_a_pub_pem: bytes,
):
    """A trailer-prefixed line with a 100 KiB hex payload → BAD_SIGNATURE.

    The parser's length bounds reject the trailer before any crypto, but
    the prefix is still present → BAD_SIGNATURE (not NO_SIGNATURE),
    distinguishing "trailer attempted but malformed" from "no trailer".
    """
    body = b"def x():\n    pass\n"
    huge_hex = b"ab" * 51200  # 100 KiB of valid lowercase hex
    file_bytes = body + b"# checkov-digest: " + huge_hex + b"\n"

    target = tmp_path / "check.py"
    target.write_bytes(file_bytes)

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])

    result, _ = verify_file(str(target), keys)
    assert result == VerificationResult.BAD_SIGNATURE


@pytest.mark.parametrize("extension", [".pyc", ".so", ".pyd", ".pyi"])
def test_binary_loadable_files_are_silently_ignored(
    extension: str, binary_loadable_dir: Path,
    key_a_pub_pem: bytes, tmp_path: Path,
):
    """Binary loadable files inside an external-checks dir are silently ignored.

    Only ``.py`` files are imported via the external-checks loader, so
    other file types (``.pyc`` / ``.so`` / ``.pyd`` / ``.pyi``) are out
    of scope for trailer signing. They must not cause the scan to fail.
    """
    (binary_loadable_dir / f"native{extension}").write_bytes(b"\x00\x01\x02")

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])

    # Must not raise — binary loadables alongside a valid signed .py are ignored.
    verified = verify_external_checks_dirs([str(binary_loadable_dir)], keys)
    assert any(p.endswith("aws_check.py") for p in verified)
    assert not any(p.endswith(extension) for p in verified)


def test_accepts_empty_init_py_signed_as_comment_only(
    tmp_path: Path, priv_a, key_a_pub_pem: bytes, make_trailer,
):
    """A signed-empty ``__init__.py`` verifies with signed_bytes == b"".

    Empty init files become exactly ``# checkov-digest: <hex>\\n`` — the
    trailer line is the entire file. The signed bytes are b"", and
    Python's package-init contract is satisfied (existence is what
    ``importlib`` checks, not contents).
    """
    root = tmp_path / "pkg"
    root.mkdir()
    init_path = root / "__init__.py"
    init_path.write_bytes(make_trailer(b"", priv_a))

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])

    result, signed_bytes = verify_file(str(init_path), keys)
    assert result == VerificationResult.OK
    assert signed_bytes == b""

    verified = verify_external_checks_dirs([str(root)], keys)
    assert verified == {str(init_path): b""}


def test_init_py_signed_as_empty_loads_as_empty_package(
    tmp_path: Path, priv_a, key_a_pub_pem: bytes, make_trailer,
):
    """The b"" returned by the verifier compiles and execs into an empty module.

    Proves the loader will get a working module object when it runs
    ``exec(compile(signed_bytes, path, "exec"), ...)`` against the empty
    init file.
    """
    init_path = tmp_path / "__init__.py"
    init_path.write_bytes(make_trailer(b"", priv_a))

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])

    result, signed_bytes = verify_file(str(init_path), keys)
    assert result == VerificationResult.OK

    code = compile(signed_bytes, str(init_path), "exec")
    namespace: dict = {}
    exec(code, namespace)  # noqa: S102 — intentional, this is the loader's contract
    user_keys = [k for k in namespace if not k.startswith("__")]
    assert user_keys == []


def test_ignores_extra_trailer_line_in_middle_of_file(
    tmp_path: Path, priv_a, key_a_pub_pem: bytes, make_trailer,
):
    """A bogus ``# checkov-digest:`` line in the middle of the file is ignored.

    Only the last line is checked. The real trailer covers the whole
    body — including any earlier digest-looking line inside it.
    """
    body = (
        b"# example trailer below for documentation:\n"
        b"# checkov-digest: deadbeef\n"
        b"def check():\n"
        b"    return 'ok'\n"
    )
    target = tmp_path / "check.py"
    target.write_bytes(make_trailer(body, priv_a))

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])

    result, signed_bytes = verify_file(str(target), keys)
    assert result == VerificationResult.OK
    assert signed_bytes == body


def test_ignores_length_valid_fake_trailer_inside_signed_body(
    tmp_path: Path, priv_a, key_a_pub_pem: bytes, make_trailer,
):
    """A LENGTH-VALID fake ``# checkov-digest:`` mid-body still verifies OK.

    Sibling to ``test_ignores_extra_trailer_line_in_middle_of_file``,
    which uses ``deadbeef`` (8 hex chars). That length is rejected by
    the parser's ``_HEX_MIN <= len <= _HEX_MAX`` (126-144) guard
    BEFORE the "only the last line counts" invariant is even
    exercised — so the existing test would pass even with a buggy
    parser that scanned every line.

    This sibling uses a 128-hex-char imposter (valid length, just not
    the real signature), proving the "last line only" rule alone
    catches the imposter even if the length filter accidentally
    accepted it. Pins the parser invariant at the right scope.
    """
    fake_trailer_line = b"# checkov-digest: " + b"ab" * 64 + b"\n"
    assert 126 <= len(b"ab" * 64) <= 144, (
        "precondition: the imposter trailer must be length-valid "
        "(otherwise we're testing the same path as the sibling test)"
    )

    body = (
        b"# real check\n"
        + fake_trailer_line  # imposter, mid-body
        + b"def check():\n    return 'ok'\n"  # real code AFTER the imposter
    )

    target = tmp_path / "imposter.py"
    target.write_bytes(make_trailer(body, priv_a))

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])

    result, signed_bytes = verify_file(str(target), keys)
    assert result == VerificationResult.OK, (
        f"length-valid mid-body fake trailer wrongly altered the result "
        f"to {result!r}; the 'last line only' rule should hold "
        f"regardless of imposter length"
    )
    assert signed_bytes == body, (
        "the verifier returned a different body than the original — the "
        "fake trailer was treated as a structural element, not data"
    )


def test_rejects_trailer_with_appended_garbage(
    tmp_path: Path, priv_a, key_a_pub_pem: bytes, make_trailer,
):
    """Junk bytes appended after the trailer's \\n → NO_SIGNATURE."""
    body = b"def check():\n    return 'ok'\n"
    target = tmp_path / "check.py"
    target.write_bytes(make_trailer(body, priv_a) + b"JUNK")

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])

    result, _ = verify_file(str(target), keys)
    assert result == VerificationResult.NO_SIGNATURE


@pytest.mark.parametrize(
    "mutation_id",
    [
        "strip_trailing_newline",
        "add_second_newline",
        "normalise_to_crlf",
    ],
)
def test_rejects_formatter_simulated_trailer_mutation(
    mutation_id: str,
    tmp_path: Path,
    priv_a,
    key_a_pub_pem: bytes,
    make_trailer,
):
    """Format-on-save style mutations all fail with a non-OK result.

    Pins the scenario where an IDE format-on-save hook corrupts the
    trailer. We assert only that the result is non-OK — the wire-format
    rules return a non-OK result in several ways for these mutations,
    and pinning the exact result per mutation would over-fit the test
    to parser internals.

    If any mutation ever returns OK silently, customers' signed files
    would start failing verification randomly in CI; this is the canary
    test for that regression.
    """
    body = b"def check():\n    return 'ok'\n"
    signed = make_trailer(body, priv_a)

    if mutation_id == "strip_trailing_newline":
        mutated = signed.rstrip(b"\n")
    elif mutation_id == "add_second_newline":
        mutated = signed + b"\n"
    elif mutation_id == "normalise_to_crlf":
        mutated = signed.replace(b"\n", b"\r\n")
    else:
        raise AssertionError(f"unknown mutation_id {mutation_id}")

    target = tmp_path / "check.py"
    target.write_bytes(mutated)

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])

    result, signed_bytes = verify_file(str(target), keys)
    assert result != VerificationResult.OK, (
        f"mutation {mutation_id!r} was silently accepted"
    )
    assert signed_bytes == b""
