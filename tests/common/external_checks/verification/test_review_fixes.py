"""Regression tests for the issues raised in the code review.

Each test below corresponds to a specific item from
``plans/cli/sig-validation/external-checks/review-checkov-external-checks-signing.md``.
The intent is one self-contained file per review pass so that future
review iterations can be added as ``test_review_fixes_<round>.py``
without disturbing the original behavioural suite.

Sections, in order:

1. **MUST-FIX:** verification failure bypasses ``--no-fail-on-crash``
2. **SHOULD-FIX:** realpath/symlink consistency between the registry
   and the loader
3. **SHOULD-FIX:** double-trailer detection produces ``DOUBLE_TRAILER``
4. **SHOULD-FIX:** stderr truncation on very large failure lists
5. **SHOULD-FIX:** v1 same-stem-checks behaviour is pinned
6. **SHOULD-FIX:** large tree with one bad file in the middle is fully
   walked (no short-circuit)
7. **Coverage gap:** env-var key parsing
8. **Coverage gap:** NUL bytes in trailer payload
"""
from __future__ import annotations

import io
import os
import sys
import types
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from checkov.common.external_checks.verification import (
    SignatureVerificationError,
    VerificationResult,
    load_public_keys,
    verify_bytes,
    verify_external_checks_dirs,
    verify_file,
)
from checkov.common.external_checks.verification.sources_registry import (
    is_verification_active,
    reset_for_tests,
    verify_and_register,
)


@pytest.fixture(autouse=True)
def _reset_registry():
    """Every test in this module starts and ends with a clean registry."""
    reset_for_tests()
    try:
        yield
    finally:
        reset_for_tests()


# --------------------------------------------------------------------------
# 1. MUST-FIX: --no-fail-on-crash MUST NOT mask a verification failure.
# --------------------------------------------------------------------------


def test_no_fail_on_crash_does_not_mask_verification_failure(
    unsigned_dir: Path, key_a_pub_pem: bytes, tmp_path: Path,
):
    """A tampered/unsigned tree must exit 2 even when --no-fail-on-crash is set.

    ``--no-fail-on-crash`` / ``CKV_NO_FAIL_ON_CRASH`` is intended for
    "the scanner itself crashed; don't fail CI on infrastructure flakes"
    — not "the scanner refused to run because it detected tampering".
    The chokepoint at ``main.py:get_external_checks_dir`` must bypass
    ``self.exit_run()`` (which honours the flag) and call ``sys.exit(2)``
    directly so the flag cannot mask a security failure.
    """
    from checkov.main import Checkov

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)

    instance = Checkov.__new__(Checkov)
    instance.config = types.SimpleNamespace(  # type: ignore[attr-defined]
        external_checks_dir=[str(unsigned_dir)],
        external_checks_public_key=[str(key_path)],
        external_checks_git=None,
        no_fail_on_crash=True,  # <-- the flag that MUST be ignored on verification failure
    )

    # Run from inside tmp_path so the side-effect log file doesn't litter
    # the repo root.
    with patch("checkov.main.bc_integration") as bc, patch("os.getcwd", return_value=str(tmp_path)):
        bc.sast_custom_policies = None
        # cwd matters because the failure-log file is written relative to cwd.
        prev_cwd = os.getcwd()
        os.chdir(str(tmp_path))
        try:
            with pytest.raises(SystemExit) as raised:
                instance.get_external_checks_dir()
        finally:
            os.chdir(prev_cwd)

    assert raised.value.code == 2, (
        "verification failure with --no-fail-on-crash must still exit 2; "
        f"got exit code {raised.value.code!r}"
    )


def test_no_fail_on_crash_off_also_exits_2(
    unsigned_dir: Path, key_a_pub_pem: bytes, tmp_path: Path,
):
    """Companion to the previous test: with the flag OFF, still exit 2.

    Pins that the unconditional ``sys.exit(2)`` is exit 2 in both flag
    states. If a future refactor accidentally inverts the flag check,
    this test catches it.
    """
    from checkov.main import Checkov

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)

    instance = Checkov.__new__(Checkov)
    instance.config = types.SimpleNamespace(  # type: ignore[attr-defined]
        external_checks_dir=[str(unsigned_dir)],
        external_checks_public_key=[str(key_path)],
        external_checks_git=None,
        no_fail_on_crash=False,
    )
    with patch("checkov.main.bc_integration") as bc:
        bc.sast_custom_policies = None
        prev_cwd = os.getcwd()
        os.chdir(str(tmp_path))
        try:
            with pytest.raises(SystemExit) as raised:
                instance.get_external_checks_dir()
        finally:
            os.chdir(prev_cwd)
    assert raised.value.code == 2


def test_exit_run_after_verification_failure_still_exits_2(
    unsigned_dir: Path, key_a_pub_pem: bytes, tmp_path: Path,
):
    """Once verification has failed, *every* subsequent ``exit_run()``
    call must exit 2, even when ``--no-fail-on-crash`` is set.

    This pins the sticky ``_security_failure_exit_pending`` flag. The
    outer ``except SystemExit`` handler in ``Checkov.run`` calls
    ``self.exit_run()`` after our chokepoint raises ``SystemExit(2)`` —
    without the sticky flag, that re-call would silently downgrade the
    exit to 0 under ``--no-fail-on-crash``. Caught by real end-to-end
    testing: the unit test that only invoked ``get_external_checks_dir``
    in isolation missed it.
    """
    from checkov.main import Checkov

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)

    instance = Checkov.__new__(Checkov)
    instance.config = types.SimpleNamespace(  # type: ignore[attr-defined]
        external_checks_dir=[str(unsigned_dir)],
        external_checks_public_key=[str(key_path)],
        external_checks_git=None,
        no_fail_on_crash=True,
    )

    # Step 1: chokepoint sets the flag and exits 2.
    with patch("checkov.main.bc_integration") as bc:
        bc.sast_custom_policies = None
        prev_cwd = os.getcwd()
        os.chdir(str(tmp_path))
        try:
            with pytest.raises(SystemExit) as raised_first:
                instance.get_external_checks_dir()
        finally:
            os.chdir(prev_cwd)
    assert raised_first.value.code == 2

    # Step 2: simulate the outer wrapper's "re-exit cleanly" call.
    # Without the sticky flag, this would exit 0 because
    # no_fail_on_crash=True. With the flag, it must still exit 2.
    with pytest.raises(SystemExit) as raised_second:
        instance.exit_run()
    assert raised_second.value.code == 2, (
        "exit_run() after a verification failure must exit 2 regardless "
        "of --no-fail-on-crash; got "
        f"exit code {raised_second.value.code!r}. The sticky "
        "_security_failure_exit_pending flag is the only thing preventing "
        "the outer ``except SystemExit`` handler in Checkov.run from "
        "silently downgrading the security exit to 0."
    )


def test_exit_run_without_security_failure_honours_no_fail_on_crash(tmp_path: Path):
    """Regression guard for the previous test: an ordinary ``exit_run``
    call (no verification involved) still honours ``--no-fail-on-crash``.

    The sticky flag must default to *unset* so the pre-existing semantic
    of ``--no-fail-on-crash`` for genuine scanner crashes is preserved.
    """
    from checkov.main import Checkov

    instance = Checkov.__new__(Checkov)
    instance.config = types.SimpleNamespace(  # type: ignore[attr-defined]
        no_fail_on_crash=True,
    )
    with pytest.raises(SystemExit) as raised:
        instance.exit_run()
    assert raised.value.code == 0, (
        "without the security-failure sentinel, exit_run() must still "
        "honour --no-fail-on-crash for ordinary scanner crashes; got "
        f"{raised.value.code!r}"
    )


# --------------------------------------------------------------------------
# 2. SHOULD-FIX: realpath/symlink consistency between the registry and the
#    loader. Verifies the fix for the case where ``--external-checks-dir``
#    is itself a symlink to a verified tree.
# --------------------------------------------------------------------------


def test_verified_load_works_when_external_checks_dir_is_symlinked(
    tmp_path: Path, priv_a, key_a_pub_pem: bytes, make_trailer,
):
    """``--external-checks-dir`` pointed at a symlink must still resolve.

    Before the fix: ``verify_and_register`` realpath-normalised the
    allowlist keys, but the loader looked them up by the raw (symlinked)
    ``entry.path`` and missed → "Refusing to load unverified external check".
    The fix realpath-normalises the candidate path inside the loader so
    the comparison is canonical regardless of how the user spelled the
    top-level directory.
    """
    # Real directory with a signed check.
    real_dir = tmp_path / "real_checks"
    real_dir.mkdir()
    (real_dir / "__init__.py").write_bytes(make_trailer(b"", priv_a))
    body = b"# signed via symlinked dir\nCHECK_ID = 'CKV_T_42'\n"
    (real_dir / "checked.py").write_bytes(make_trailer(body, priv_a))

    # Symlink pointing at it.
    symlinked = tmp_path / "symlinked_checks"
    try:
        os.symlink(real_dir, symlinked)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks not supported on this platform")

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)

    # Register via the symlinked path — this is what the user passes
    # on the command line.
    verify_and_register([str(symlinked)], [str(key_path)])
    assert is_verification_active() is True

    # Now drive the loader against the symlinked path (which is what
    # the runners will do — they don't realpath the user input either).
    from checkov.common.checks.base_check_registry import BaseCheckRegistry

    class _StubRegistry(BaseCheckRegistry):
        def extract_entity_details(self, entity):
            return ("", "", {})

    registry = _StubRegistry(report_type="terraform")

    # Capture stderr to confirm no "Refusing to load" error log appears.
    import logging
    caplog_records: list[logging.LogRecord] = []

    class _Capture(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            caplog_records.append(record)

    handler = _Capture()
    logging.getLogger().addHandler(handler)
    try:
        registry.load_external_checks(str(symlinked))
    finally:
        logging.getLogger().removeHandler(handler)

    refusals = [
        r for r in caplog_records
        if "Refusing to load unverified external check" in r.getMessage()
    ]
    assert not refusals, (
        f"loader refused a signed file when --external-checks-dir was "
        f"itself a symlink; refusal messages: "
        f"{[r.getMessage() for r in refusals]}"
    )


# --------------------------------------------------------------------------
# 3. SHOULD-FIX: double-trailer detection produces DOUBLE_TRAILER.
# --------------------------------------------------------------------------


def test_double_trailer_returns_dedicated_result_code(
    tmp_path: Path, priv_a, key_a_pub_pem: bytes, make_trailer,
):
    """A file with two trailer lines at the end → ``DOUBLE_TRAILER``.

    Before the fix this returned ``UNKNOWN_KEY`` (well-formed sig, doesn't
    verify), which was a confusing diagnostic for an operator who just
    accidentally ran the signing recipe twice. The dedicated result code
    means the customer-facing error message can say "you signed this
    twice" instead of "signature verification failed".
    """
    body = b"def check():\n    return 'ok'\n"
    singly_signed = make_trailer(body, priv_a)
    # Run the signing recipe a second time, naively, on the already-signed file.
    doubly_signed = make_trailer(singly_signed, priv_a)

    target = tmp_path / "double_signed.py"
    target.write_bytes(doubly_signed)

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])

    result, signed_bytes = verify_file(str(target), keys)
    assert result == VerificationResult.DOUBLE_TRAILER, (
        f"expected DOUBLE_TRAILER, got {result!r}"
    )
    assert signed_bytes == b""


def test_double_trailer_is_reported_with_actionable_message(
    tmp_path: Path, priv_a, key_a_pub_pem: bytes, make_trailer,
):
    """The enforce-layer error message names the file and the cause."""
    root = tmp_path / "double_signed_dir"
    root.mkdir()
    (root / "__init__.py").write_bytes(make_trailer(b"", priv_a))
    body = b"def check():\n    return 'ok'\n"
    singly_signed = make_trailer(body, priv_a)
    doubly_signed = make_trailer(singly_signed, priv_a)
    (root / "twice_signed.py").write_bytes(doubly_signed)

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])

    with pytest.raises(SignatureVerificationError) as exc:
        verify_external_checks_dirs([str(root)], keys)

    msg = str(exc.value)
    assert "twice_signed.py" in msg
    assert "signed twice" in msg.lower()


def test_legitimate_signed_file_with_digest_text_in_body_is_not_flagged(
    tmp_path: Path, priv_a, key_a_pub_pem: bytes, make_trailer,
):
    """A signed file with the literal ``# checkov-digest:`` *inside* the body
    (e.g. as a documentation example) must verify normally, not be confused
    with a double-trailer.

    Only the two FINAL lines matter for the double-trailer check.
    """
    # The fake-trailer line appears mid-body, then non-trailer code follows,
    # then the real trailer.
    body = (
        b"# example trailer below for documentation:\n"
        b"# checkov-digest: deadbeef\n"
        b"def check():\n"
        b"    return 'ok'\n"
    )
    target = tmp_path / "doc_example.py"
    target.write_bytes(make_trailer(body, priv_a))

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])

    result, signed_bytes = verify_file(str(target), keys)
    assert result == VerificationResult.OK
    assert signed_bytes == body


# --------------------------------------------------------------------------
# 4. SHOULD-FIX: stderr truncation on huge failure lists.
# --------------------------------------------------------------------------


def test_stderr_truncated_on_huge_failure_list(
    tmp_path: Path, key_a_pub_pem: bytes,
):
    """A 100-bad-file failure prints ~20 inline lines plus a "... N more" hint.

    The full list is written to ``./checkov-verification-failures.log``
    so nothing is lost.
    """
    from checkov.main import Checkov

    big = tmp_path / "many_unsigned"
    big.mkdir()
    for i in range(100):
        (big / f"check_{i:03d}.py").write_bytes(b"# unsigned\n")

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)

    instance = Checkov.__new__(Checkov)
    instance.config = types.SimpleNamespace(  # type: ignore[attr-defined]
        external_checks_dir=[str(big)],
        external_checks_public_key=[str(key_path)],
        external_checks_git=None,
        no_fail_on_crash=False,
    )

    # Capture stderr by patching sys.stderr to a StringIO.
    captured = io.StringIO()
    with patch("checkov.main.bc_integration") as bc, patch("sys.stderr", captured):
        bc.sast_custom_policies = None
        prev_cwd = os.getcwd()
        os.chdir(str(tmp_path))
        try:
            with pytest.raises(SystemExit) as raised:
                instance.get_external_checks_dir()
        finally:
            os.chdir(prev_cwd)

    assert raised.value.code == 2
    stderr_text = captured.getvalue()

    # Hard upper bound on inline failure lines (header + ~20 visible + truncation hint).
    visible_failure_lines = [
        ln for ln in stderr_text.split("\n") if ln.strip().startswith("- missing signature:")
    ]
    assert len(visible_failure_lines) <= 25, (
        f"stderr printed {len(visible_failure_lines)} inline failure lines; "
        f"expected ~20 with a truncation hint"
    )
    assert "... and" in stderr_text and "more" in stderr_text, (
        "expected a 'and N more' truncation hint on stderr"
    )

    # Full-list log file exists and contains all 100 entries.
    log_path = tmp_path / "checkov-verification-failures.log"
    assert log_path.exists(), "expected ./checkov-verification-failures.log to be written"
    log_text = log_path.read_text()
    assert log_text.count("missing signature:") == 100


def test_stderr_not_truncated_when_failure_list_is_short(
    unsigned_dir: Path, key_a_pub_pem: bytes, tmp_path: Path,
):
    """A 1-bad-file failure prints the whole list inline, no truncation hint."""
    from checkov.main import Checkov

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    instance = Checkov.__new__(Checkov)
    instance.config = types.SimpleNamespace(  # type: ignore[attr-defined]
        external_checks_dir=[str(unsigned_dir)],
        external_checks_public_key=[str(key_path)],
        external_checks_git=None,
        no_fail_on_crash=False,
    )

    captured = io.StringIO()
    with patch("checkov.main.bc_integration") as bc, patch("sys.stderr", captured):
        bc.sast_custom_policies = None
        prev_cwd = os.getcwd()
        os.chdir(str(tmp_path))
        try:
            with pytest.raises(SystemExit):
                instance.get_external_checks_dir()
        finally:
            os.chdir(prev_cwd)

    assert "... and" not in captured.getvalue()


# --------------------------------------------------------------------------
# 5. SHOULD-FIX: pin v1 behaviour for same-stem checks across subdirectories.
# --------------------------------------------------------------------------


def test_same_stem_checks_in_subdirectories_collide_deterministically(
    tmp_path: Path, priv_a, key_a_pub_pem: bytes, make_trailer,
):
    """Two ``helper.py`` files in different subdirectories collide on ``helper``.

    This is a v1 limitation documented in the customer-facing docs.
    The test pins the behaviour so a future refactor that "fixes" the
    collision unintentionally is flagged. The exact winner is not part
    of the contract — the test only asserts that *one* of them wins
    deterministically and the other is shadowed, not that both load
    side by side.
    """
    from checkov.common.checks.base_check_registry import BaseCheckRegistry

    root = tmp_path / "root"
    root.mkdir()
    (root / "__init__.py").write_bytes(make_trailer(b"", priv_a))

    aws = root / "aws"
    aws.mkdir()
    (aws / "__init__.py").write_bytes(make_trailer(b"", priv_a))
    (aws / "helper.py").write_bytes(make_trailer(b"PROVIDER = 'aws'\n", priv_a))

    azure = root / "azure"
    azure.mkdir()
    (azure / "__init__.py").write_bytes(make_trailer(b"", priv_a))
    (azure / "helper.py").write_bytes(make_trailer(b"PROVIDER = 'azure'\n", priv_a))

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    verify_and_register([str(root)], [str(key_path)])

    class _StubRegistry(BaseCheckRegistry):
        def extract_entity_details(self, entity):
            return ("", "", {})

    registry = _StubRegistry(report_type="terraform")

    # Clean any pre-existing 'helper' module so the test isn't polluted.
    sys.modules.pop("helper", None)
    try:
        registry.load_external_checks(str(root))
        # Exactly one 'helper' wins.
        assert "helper" in sys.modules, "expected 'helper' to be registered"
        winner = sys.modules["helper"]
        assert getattr(winner, "PROVIDER", None) in ("aws", "azure"), (
            "the collision did not produce a single deterministic winner — "
            "v1 behaviour assumed by the docs has changed"
        )
    finally:
        sys.modules.pop("helper", None)


# --------------------------------------------------------------------------
# 6. SHOULD-FIX: large tree with one bad file in the middle is fully walked.
# --------------------------------------------------------------------------


def test_large_tree_with_one_bad_file_does_not_short_circuit(
    tmp_path: Path, priv_a, key_a_pub_pem: bytes, make_trailer,
):
    """Verification must walk the whole tree even after a bad file.

    Pins that a single bad file does NOT short-circuit verification —
    a customer with 1 000 files and one accidental unsigned addition
    should still get a single error listing exactly that file, not
    "stopped scanning after first failure".
    """
    root = tmp_path / "big_tree"
    root.mkdir()
    (root / "__init__.py").write_bytes(make_trailer(b"", priv_a))
    # 200 signed files (plenty to confirm we walked past the bad one).
    for i in range(200):
        body = f"# signed {i}\nID = 'CKV_T_{i:04d}'\n".encode("ascii")
        (root / f"signed_{i:03d}.py").write_bytes(make_trailer(body, priv_a))
    # One unsigned file in the middle of the alphabetical ordering.
    (root / "signed_099_BAD.py").write_bytes(b"# unsigned\n")
    # And one more signed file later, to prove we kept walking.
    (root / "zzz_last_signed.py").write_bytes(
        make_trailer(b"# last\nID = 'LAST'\n", priv_a)
    )

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])

    with pytest.raises(SignatureVerificationError) as exc:
        verify_external_checks_dirs([str(root)], keys)

    msg = str(exc.value)
    # Exactly one failure line — for the one bad file.
    failure_lines = [
        ln for ln in msg.split("\n") if "missing signature" in ln
    ]
    assert len(failure_lines) == 1
    assert "signed_099_BAD.py" in failure_lines[0]


def test_many_bad_files_all_reported(
    tmp_path: Path, priv_a, key_a_pub_pem: bytes,
):
    """All bad files across a dir surface in one cycle — no short-circuit."""
    root = tmp_path / "all_bad"
    root.mkdir()
    for i in range(50):
        (root / f"bad_{i:02d}.py").write_bytes(b"# unsigned\n")

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])

    with pytest.raises(SignatureVerificationError) as exc:
        verify_external_checks_dirs([str(root)], keys)
    msg = str(exc.value)
    # Every single bad file must be named in the failure list.
    for i in range(50):
        assert f"bad_{i:02d}.py" in msg, (
            f"bad_{i:02d}.py was not reported — verification short-circuited"
        )


# --------------------------------------------------------------------------
# 7. Coverage gap: env-var key parsing.
# --------------------------------------------------------------------------


def test_public_key_env_var_parses_single_path(monkeypatch):
    """``CKV_EXTERNAL_CHECKS_PUBLIC_KEY=/x.pem`` parses to one-element list."""
    from checkov.common.util.ext_argument_parser import ExtArgumentParser

    monkeypatch.setenv("CKV_EXTERNAL_CHECKS_PUBLIC_KEY", "/tmp/single.pem")
    parser = ExtArgumentParser(description="test")
    parser.add_parser_args()
    cfg = parser.parse_args([])
    assert cfg.external_checks_public_key == ["/tmp/single.pem"]


def test_public_key_cli_overrides_env_var(monkeypatch):
    """CLI flag takes precedence over env var (configargparse semantics)."""
    from checkov.common.util.ext_argument_parser import ExtArgumentParser

    monkeypatch.setenv("CKV_EXTERNAL_CHECKS_PUBLIC_KEY", "/tmp/from-env.pem")
    parser = ExtArgumentParser(description="test")
    parser.add_parser_args()
    cfg = parser.parse_args(
        ["--external-checks-public-key", "/tmp/from-cli.pem"],
    )
    # CLI wins; env value should not be silently appended.
    assert "/tmp/from-cli.pem" in cfg.external_checks_public_key
    assert "/tmp/from-env.pem" not in cfg.external_checks_public_key


# --------------------------------------------------------------------------
# 8. Coverage gap: NUL bytes in trailer payload.
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "byte",
    [
        b"\x00",   # NUL — common "smuggling" attempt
        b"\xff",   # high byte
        b"\x7f",   # DEL
        b" ",      # ASCII space inside the hex blob
        b"\t",     # tab
        b"g",      # outside the hex alphabet
        b"G",      # uppercase hex variant (would be valid hex but we disallow uppercase)
    ],
)
def test_trailer_payload_rejects_non_hex_bytes(
    byte: bytes, tmp_path: Path, priv_a, key_a_pub_pem: bytes, make_sign,
):
    """Any non-lowercase-hex byte in the hex payload → ``BAD_SIGNATURE``.

    Pins the alphabet guard. A regression in
    ``trailer_format._LOWERCASE_HEX_BYTES`` (e.g. someone "helpfully"
    adds uppercase) would silently broaden the parser surface; this
    parametrised test names every disallowed character class.
    """
    body = b"def x():\n    pass\n"
    sig_der = make_sign(priv_a, body)
    hex_payload = sig_der.hex().encode("ascii")
    # Replace one character in the middle of the otherwise-valid hex
    # payload with the disallowed byte. (Position chosen well inside the
    # payload so the length-range guard still passes.)
    mutated_payload = hex_payload[:10] + byte + hex_payload[11:]
    file_bytes = body + b"# checkov-digest: " + mutated_payload + b"\n"

    target = tmp_path / "bad.py"
    target.write_bytes(file_bytes)

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])

    result, _ = verify_file(str(target), keys)
    assert result == VerificationResult.BAD_SIGNATURE, (
        f"byte {byte!r} in trailer payload should be rejected; got {result!r}"
    )


def test_trailer_payload_inside_signed_body_not_treated_as_trailer(
    tmp_path: Path, priv_a, key_a_pub_pem: bytes, make_trailer,
):
    """A literal ``\\x00`` inside the signed *body* must not affect verification.

    The body bytes are opaque to the trailer parser; only the trailer
    line's bytes are subject to the alphabet guard. Without this
    invariant a check that legitimately contains a NUL byte (e.g.
    a binary blob in a docstring) couldn't be signed.
    """
    body = b"# binary marker:\nDATA = b'\\x00\\x01\\x02'\n"
    target = tmp_path / "binary_body.py"
    target.write_bytes(make_trailer(body, priv_a))

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])

    result, signed_bytes = verify_file(str(target), keys)
    assert result == VerificationResult.OK
    assert signed_bytes == body


# --------------------------------------------------------------------------
# 9. Regression caught during end-to-end testing: the LEGACY path
#    (no public key configured) must NOT require the ``cryptography``
#    package.
#
#    ``cryptography`` is NOT a core checkov dependency. It is only
#    required when the operator opts into verification by passing
#    ``--external-checks-public-key``. If the package ``__init__.py``
#    eagerly re-exports the crypto-touching submodules, every existing
#    user of ``--external-checks-dir`` (including users who never
#    enabled signing) breaks with ``ModuleNotFoundError: No module named
#    'cryptography'`` on a stock install — a silent backward-compat
#    regression.
#
#    The fix is PEP 562 lazy attributes on the package ``__init__.py``.
#    These tests run in a subprocess with ``cryptography`` hidden from
#    the import system so a regression here is caught directly.
# --------------------------------------------------------------------------


def _run_in_subprocess_without_cryptography(
    script: str, tmp_path: Path,
) -> "tuple[int, str, str]":
    """Run ``script`` in a fresh Python process that cannot import ``cryptography``.

    Uses a ``sitecustomize.py`` trick: Python automatically imports a
    module called ``sitecustomize`` at startup if it exists on the path,
    BEFORE any user code runs. We drop one on ``PYTHONPATH`` that
    installs a ``sys.meta_path`` finder which raises
    ``ModuleNotFoundError`` for ``cryptography`` and any of its
    subpackages. The subprocess therefore sees the same Python
    environment as the test, MINUS ``cryptography``.

    Returns ``(returncode, stdout, stderr)``.
    """
    import subprocess
    blocker_dir = tmp_path / "_blocker"
    blocker_dir.mkdir()
    (blocker_dir / "sitecustomize.py").write_text(
        "import sys\n"
        "class _Blocker:\n"
        "    def find_spec(self, fullname, path=None, target=None):\n"
        "        if fullname == 'cryptography' or fullname.startswith('cryptography.'):\n"
        "            raise ModuleNotFoundError(\n"
        "                f'simulated: {fullname} blocked for test'\n"
        "            )\n"
        "        return None\n"
        "sys.meta_path.insert(0, _Blocker())\n"
    )
    script_path = tmp_path / "_run.py"
    script_path.write_text(script)
    env = dict(os.environ)
    env["PYTHONPATH"] = str(blocker_dir) + os.pathsep + env.get("PYTHONPATH", "")
    result = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True,
        text=True,
        env=env,
        timeout=30,
    )
    return result.returncode, result.stdout, result.stderr


def test_package_import_does_not_require_cryptography(tmp_path: Path):
    """Importing the verification package must not transitively import ``cryptography``.

    Pins the PEP 562 lazy ``__getattr__`` design: a bare
    ``import checkov.common.external_checks.verification`` must succeed
    on a Python environment that does not have ``cryptography``
    installed. ``dir()`` on the package must also not trigger any
    crypto-touching submodule import.
    """
    script = (
        "import sys\n"
        "# Confirm the blocker is actually in effect — guards against a\n"
        "# silent test-harness regression where the subprocess somehow\n"
        "# still finds cryptography.\n"
        "try:\n"
        "    import cryptography  # noqa\n"
        "    raise SystemExit('TEST_HARNESS_BROKEN: cryptography is importable')\n"
        "except ModuleNotFoundError:\n"
        "    pass\n"
        "# Now the real assertion: importing the verification package must work.\n"
        "import checkov.common.external_checks.verification as v\n"
        "# And reading the documented public names via __dir__ must not\n"
        "# trigger the crypto submodules either.\n"
        "names = dir(v)\n"
        "assert 'SignatureVerificationError' in names\n"
        "assert 'verify_external_checks_dirs' in names\n"
        "print('OK')\n"
    )
    rc, stdout, stderr = _run_in_subprocess_without_cryptography(script, tmp_path)
    assert rc == 0, (
        f"package import failed when cryptography was unavailable\n"
        f"--- stdout ---\n{stdout}\n--- stderr ---\n{stderr}"
    )
    assert "OK" in stdout


def test_legacy_load_external_checks_works_without_cryptography(tmp_path: Path):
    """Loading an external check with no public key configured must work
    on a Python install without ``cryptography``.

    This is the backward-compat contract for every existing user of
    ``--external-checks-dir``. Caught by real end-to-end testing — the
    unit tests had ``cryptography`` available in the test venv and
    missed the eager-import regression.
    """
    # Build a tiny unsigned check tree the loader can scan.
    checks_dir = tmp_path / "checks"
    checks_dir.mkdir()
    (checks_dir / "__init__.py").write_bytes(b"")
    (checks_dir / "demo_unsigned_check.py").write_bytes(
        b"# unsigned check, legacy path\n"
        b"LOADED = True\n"
    )
    script = (
        f"import sys\n"
        f"# Confirm the blocker is in effect.\n"
        f"try:\n"
        f"    import cryptography  # noqa\n"
        f"    raise SystemExit('TEST_HARNESS_BROKEN: cryptography is importable')\n"
        f"except ModuleNotFoundError:\n"
        f"    pass\n"
        f"from checkov.common.checks.base_check_registry import BaseCheckRegistry\n"
        f"class _StubRegistry(BaseCheckRegistry):\n"
        f"    def extract_entity_details(self, entity):\n"
        f"        return ('', '', {{}})\n"
        f"registry = _StubRegistry(report_type='terraform')\n"
        f"registry.load_external_checks({str(checks_dir.resolve())!r})\n"
        f"# Confirm the check actually loaded (legacy disk-exec path).\n"
        f"import demo_unsigned_check\n"
        f"assert demo_unsigned_check.LOADED is True\n"
        f"print('OK')\n"
    )
    rc, stdout, stderr = _run_in_subprocess_without_cryptography(script, tmp_path)
    assert rc == 0, (
        f"legacy load_external_checks crashed when cryptography was "
        f"unavailable — a backward-compat regression\n"
        f"--- stdout ---\n{stdout}\n--- stderr ---\n{stderr}"
    )
    assert "OK" in stdout


# --------------------------------------------------------------------------
# 10. Regression caught during end-to-end testing: ``__pycache__/``
#     handling. Caught the same way as the cryptography-not-installed
#     regression — by running the real CLI end-to-end. After a verified
#     scan, CPython would leave behind ``__pycache__/<name>.cpython-XYZ.pyc``
#     files. The next verified scan against the same directory would
#     then hard-reject the whole dir with "binary file not supported
#     under trailer signing" — a false positive on a cache file the
#     user never created.
#
#     The fix is two-pronged:
#     a) The walker silently skips ``__pycache__`` subdirectories.
#     b) The loader sets ``sys.dont_write_bytecode = True`` for the
#        load window so no fresh caches appear in the first place.
# --------------------------------------------------------------------------


def test_walker_skips_pycache_subdirectory(
    tmp_path: Path, priv_a, key_a_pub_pem: bytes, make_trailer,
):
    """A pre-existing ``__pycache__/*.pyc`` next to signed sources is silently skipped.

    Pre-existing caches arise from local development, prior non-verified
    scans, or any tooling that imports the source. Treating them as a
    verification failure would force every user to delete
    ``__pycache__`` before every run.
    """
    root = tmp_path / "with_pycache"
    root.mkdir()
    (root / "__init__.py").write_bytes(make_trailer(b"", priv_a))
    (root / "check.py").write_bytes(
        make_trailer(b"# signed check\nID = 'CKV_T_1'\n", priv_a)
    )
    # Drop a realistic-looking stray .pyc into __pycache__.
    cache = root / "__pycache__"
    cache.mkdir()
    (cache / "check.cpython-313.pyc").write_bytes(b"\x00\x01\x02pretend bytecode")

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])

    # Must not raise — the .pyc inside __pycache__ is ignored.
    verified = verify_external_checks_dirs([str(root)], keys)
    assert any(p.endswith("check.py") for p in verified)
    # And the .pyc must NOT have been added to the allowlist either —
    # the loader would refuse it on import, but we shouldn't even
    # consider it a candidate.
    assert not any(p.endswith(".pyc") for p in verified)


def test_pyc_outside_pycache_is_still_hard_rejected(
    tmp_path: Path, priv_a, key_a_pub_pem: bytes, make_trailer,
):
    """A ``.pyc`` that is NOT under ``__pycache__/`` is still a hard failure.

    Skipping all ``.pyc`` files everywhere would create a way to ship
    an unverified ``.pyc`` next to a signed ``.py`` by placing it
    outside any cache directory. The skip is strictly scoped to the
    ``__pycache__`` directory name.
    """
    root = tmp_path / "loose_pyc"
    root.mkdir()
    (root / "__init__.py").write_bytes(make_trailer(b"", priv_a))
    (root / "check.py").write_bytes(make_trailer(b"# signed\n", priv_a))
    # A stray .pyc at top-level — NOT inside __pycache__.
    (root / "rogue.pyc").write_bytes(b"\x00\x01\x02")

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])

    with pytest.raises(SignatureVerificationError) as exc:
        verify_external_checks_dirs([str(root)], keys)
    assert "rogue.pyc" in str(exc.value)


def test_verified_load_does_not_create_pycache(
    tmp_path: Path, priv_a, key_a_pub_pem: bytes, make_trailer,
):
    """A successful verified load must not leave a ``__pycache__/`` behind.

    Pins the ``sys.dont_write_bytecode = True`` window. Without this,
    every verified scan would seed the next scan's false-positive
    ``binary file not supported`` failure (see the regression that
    surfaced during end-to-end testing).
    """
    from checkov.common.checks.base_check_registry import BaseCheckRegistry

    root = tmp_path / "fresh"
    root.mkdir()
    (root / "__init__.py").write_bytes(make_trailer(b"", priv_a))
    (root / "fresh_check.py").write_bytes(
        make_trailer(b"# signed\nID = 'CKV_FRESH'\n", priv_a)
    )

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    verify_and_register([str(root)], [str(key_path)])

    class _StubRegistry(BaseCheckRegistry):
        def extract_entity_details(self, entity):
            return ("", "", {})

    sys.modules.pop("fresh_check", None)
    try:
        _StubRegistry(report_type="terraform").load_external_checks(str(root))
    finally:
        sys.modules.pop("fresh_check", None)

    pycache = root / "__pycache__"
    assert not pycache.exists(), (
        f"verified load created a __pycache__ directory; should have been "
        f"prevented by sys.dont_write_bytecode. Contents: "
        f"{list(pycache.iterdir()) if pycache.exists() else 'N/A'}"
    )


def test_dont_write_bytecode_state_restored_after_load(
    tmp_path: Path, priv_a, key_a_pub_pem: bytes, make_trailer,
):
    """``sys.dont_write_bytecode`` returns to its pre-call value after load.

    The verified-load window must not permanently silence bytecode
    writing for the rest of the process.
    """
    from checkov.common.checks.base_check_registry import BaseCheckRegistry

    root = tmp_path / "restore_test"
    root.mkdir()
    (root / "__init__.py").write_bytes(make_trailer(b"", priv_a))
    (root / "check.py").write_bytes(make_trailer(b"# signed\n", priv_a))

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    verify_and_register([str(root)], [str(key_path)])

    class _StubRegistry(BaseCheckRegistry):
        def extract_entity_details(self, entity):
            return ("", "", {})

    # Exercise both starting values to confirm the restore is faithful.
    for initial in (False, True):
        previous = sys.dont_write_bytecode
        sys.dont_write_bytecode = initial
        sys.modules.pop("check", None)
        try:
            _StubRegistry(report_type="terraform").load_external_checks(str(root))
            assert sys.dont_write_bytecode is initial, (
                f"sys.dont_write_bytecode not restored — was {initial}, "
                f"became {sys.dont_write_bytecode}"
            )
        finally:
            sys.dont_write_bytecode = previous
            sys.modules.pop("check", None)
