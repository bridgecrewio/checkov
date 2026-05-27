"""Regression tests for the verification feature.

Each section covers one behavioural contract; the section headers are
functional groupings only, not TODOs.
"""
from __future__ import annotations

import io
import os
import sys
import types
from pathlib import Path
from unittest.mock import patch

import pytest

from checkov.common.external_checks.verification import (
    SignatureVerificationError,
    VerificationResult,
    load_public_keys,
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
# 1. --no-fail-on-crash behaviour for verification failures.
#
# Contract (matches the documented help text "Return exit code 0 instead of 2"):
#   * Flag OFF -> exit 2, stderr message printed, ./checkov-verification-failures.log written.
#   * Flag ON  -> exit 0, SAME stderr message + SAME log file.
# The flag changes ONLY the exit code, not the diagnostic surface.
# --------------------------------------------------------------------------


def _run_chokepoint(
    unsigned_dir: Path, key_a_pub_pem: bytes, tmp_path: Path,
    *, no_fail_on_crash: bool,
) -> "tuple[int, str]":
    """Run the chokepoint with a tampered tree; return ``(exit_code, stderr_text)``."""
    from checkov.main import Checkov
    import io
    import contextlib

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)

    instance = Checkov.__new__(Checkov)
    instance.config = types.SimpleNamespace(  # type: ignore[attr-defined]
        external_checks_dir=[str(unsigned_dir)],
        external_checks_public_key=[str(key_path)],
        external_checks_git=None,
        no_fail_on_crash=no_fail_on_crash,
    )

    captured_stderr = io.StringIO()
    with patch("checkov.main.bc_integration") as bc, \
         contextlib.redirect_stderr(captured_stderr):
        bc.sast_custom_policies = None
        prev_cwd = os.getcwd()
        os.chdir(str(tmp_path))
        try:
            with pytest.raises(SystemExit) as raised:
                instance.get_external_checks_dir()
        finally:
            os.chdir(prev_cwd)
    return raised.value.code, captured_stderr.getvalue()


def test_verification_failure_without_no_fail_on_crash_exits_2(
    unsigned_dir: Path, key_a_pub_pem: bytes, tmp_path: Path,
):
    """Default flag state: verification failure exits 2."""
    code, stderr = _run_chokepoint(
        unsigned_dir, key_a_pub_pem, tmp_path, no_fail_on_crash=False,
    )
    assert code == 2
    assert "External checks signature verification failed" in stderr
    assert (tmp_path / "checkov-verification-failures.log").exists()


def test_verification_failure_with_no_fail_on_crash_exits_0(
    unsigned_dir: Path, key_a_pub_pem: bytes, tmp_path: Path,
):
    """``--no-fail-on-crash`` aligns the security-failure exit code with the
    documented contract of the flag (``Return exit code 0 instead of 2``).

    The diagnostic surface — stderr message, failure log file on disk — is
    UNCHANGED. Only the exit code differs. Operators who need the pipeline
    to fail must either drop the flag or grep stderr / the log file.
    """
    code, stderr = _run_chokepoint(
        unsigned_dir, key_a_pub_pem, tmp_path, no_fail_on_crash=True,
    )
    assert code == 0, (
        "--no-fail-on-crash documents 'Return exit code 0 instead of 2'; "
        f"got {code!r}"
    )
    assert "External checks signature verification failed" in stderr
    assert (tmp_path / "checkov-verification-failures.log").exists()


def test_exit_run_honours_no_fail_on_crash(tmp_path: Path):
    """Sanity: ``exit_run`` is the unmodified pre-MR contract."""
    from checkov.main import Checkov

    instance = Checkov.__new__(Checkov)
    instance.config = types.SimpleNamespace(  # type: ignore[attr-defined]
        no_fail_on_crash=True,
    )
    with pytest.raises(SystemExit) as raised:
        instance.exit_run()
    assert raised.value.code == 0


def test_exit_run_has_no_security_failure_sticky_flag():
    """Pin the absence of the ``_security_failure_exit_pending`` sticky-flag.

    Earlier in this MR ``exit_run`` carried a carve-out that overrode
    ``--no-fail-on-crash`` for verification failures (always exit 2,
    even when the flag was set). That was a real design mistake — it
    silently violated the documented flag contract — and was removed.
    The e2e harness greps for this name in a preflight check, but
    e2e harnesses can be skipped in CI; this unit test guarantees
    the same invariant is enforced on every ``pytest`` run, so a
    future refactor that re-introduces a similar sticky-flag fails
    fast in the unit suite instead of in customer pipelines.
    """
    import inspect
    from checkov.main import Checkov

    src = inspect.getsource(Checkov.exit_run)
    assert "_security_failure_exit_pending" not in src, (
        "Checkov.exit_run reintroduced the sticky-flag override that was "
        "removed earlier in this MR. --no-fail-on-crash must be honoured "
        "uniformly for ALL failure types, including verification failures. "
        "Either move the security-specific exit-code logic out of exit_run "
        "or remove the sticky flag entirely."
    )


# --------------------------------------------------------------------------
# 2. Realpath / symlink consistency between the registry and the loader.
# --------------------------------------------------------------------------


def test_verified_load_works_when_external_checks_dir_is_symlinked(
    tmp_path: Path, priv_a, key_a_pub_pem: bytes, make_trailer,
):
    """``--external-checks-dir`` pointed at a symlink must still resolve.

    The registry stores realpath-normalised allowlist keys; the loader
    must realpath-normalise its candidate path before lookup so the
    comparison is canonical regardless of how the user spelled the
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
# 3. Double-trailer detection produces the dedicated DOUBLE_TRAILER code
#    (so the customer-facing message can say "you signed this twice"
#    instead of the generic "signature verification failed").
# --------------------------------------------------------------------------


def test_double_trailer_returns_dedicated_result_code(
    tmp_path: Path, priv_a, key_a_pub_pem: bytes, make_trailer,
):
    """A file with two trailer lines at the end → ``DOUBLE_TRAILER``."""
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
# 4. stderr truncation on huge failure lists keeps the inline message
#    readable; the full list still goes to the on-disk failure log.
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
# 5. v1 scope pin: same-stem checks across subdirectories collide
#    deterministically (one wins by bare module name). Documented in the
#    customer-facing docs as a v1 limitation.
# --------------------------------------------------------------------------


def test_same_stem_checks_in_subdirectories_collide_deterministically(
    tmp_path: Path, priv_a, key_a_pub_pem: bytes, make_trailer,
):
    """Two ``helper.py`` files in different subdirectories collide on ``helper``.

    The exact winner is not part of the contract — the test only asserts
    that *one* of them wins deterministically and the other is shadowed.
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
# 6. Failure accumulation: walking continues past a bad file so every
#    offender in one tree surfaces in a single error cycle.
# --------------------------------------------------------------------------


def test_large_tree_with_one_bad_file_does_not_short_circuit(
    tmp_path: Path, priv_a, key_a_pub_pem: bytes, make_trailer,
):
    """A single bad file must NOT short-circuit verification.

    A customer with 1 000 files and one accidental unsigned addition
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
# 7. Env-var key parsing (CKV_EXTERNAL_CHECKS_PUBLIC_KEY).
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
# 8. NUL / high-byte / control-byte rejection inside the trailer payload.
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
# 9. ``__pycache__/`` handling. Two-pronged:
#    a) The walker silently skips ``__pycache__`` subdirectories so a
#       stale .pyc from a previous run doesn't trip the binary-file
#       hard-reject.
#    b) The loader sets ``sys.dont_write_bytecode = True`` for the
#       load window so no fresh caches appear in the first place.
# --------------------------------------------------------------------------


def test_walker_skips_dotfile_py_files(
    tmp_path: Path, priv_a, key_a_pub_pem: bytes, make_trailer,
):
    """``.foo.py`` / ``.backup.py`` / editor swap-style dotfiles are silently
    skipped — the loader never imports them either, so requiring them to
    be signed would produce false-positive failures for everyday
    editor/CI artifacts in the user's tree.
    """
    root = tmp_path / "with_dotfiles"
    root.mkdir()
    (root / "__init__.py").write_bytes(make_trailer(b"", priv_a))
    (root / "real_check.py").write_bytes(
        make_trailer(b"# real\nID = 'CKV_T_1'\n", priv_a)
    )
    # Drop several unsigned dotfile-style ``.py`` files that the loader
    # would never look at.
    (root / ".swp.py").write_bytes(b"# editor swap\n")
    (root / ".bak.py").write_bytes(b"# backup\n")
    (root / ".hidden_helper.py").write_bytes(b"# hidden\n")

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])

    # Must not raise — dotfile ``.py`` files are silently skipped.
    verified = verify_external_checks_dirs([str(root)], keys)
    assert any(p.endswith("real_check.py") for p in verified)
    # The dotfiles must NOT be added to the allowlist.
    for unwanted in (".swp.py", ".bak.py", ".hidden_helper.py"):
        assert not any(p.endswith(unwanted) for p in verified), (
            f"{unwanted} was added to the verified allowlist; the walker "
            f"should skip dotfile-prefixed .py files entirely"
        )


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


# --------------------------------------------------------------------------
# 10. Cross-directory transitive imports during a verified load.
#
# When the operator passes two --external-checks-dir arguments, the
# loader walks them one at a time. If a verified check in dir-A imports
# a verified helper that lives in dir-B, the meta-path finder active
# during the load of dir-A MUST still resolve the dir-B helper from
# the in-memory verified bytes — NOT fall back to the default PathFinder
# which would load it from disk WITHOUT verification.
#
# This is the security-critical invariant: while ANY verified load is
# in flight, EVERY allowlisted .py — regardless of which dir registered
# it — must be served from the in-memory verified bytes. Otherwise a
# tampered on-disk helper.py in dir-B could be smuggled into the
# process via a transitive `import helper` from a verified check in
# dir-A. The bytes the verifier hashed must be the bytes the
# interpreter executes, transitively.
# --------------------------------------------------------------------------


def test_cross_dir_transitive_import_serves_in_memory_bytes(
    tmp_path: Path, priv_a, key_a_pub_pem: bytes, make_trailer,
):
    """A verified check in dir-A that imports a verified helper in dir-B
    must get the in-memory verified bytes for the helper, not the
    on-disk file.

    Regression for M1: the per-call meta-path finder used to be built
    from only the current directory's verified subset. While dir-A was
    being loaded, the finder did not know about dir-B's verified
    sources, so a transitive `import shared_helper` would miss the
    finder and the default PathFinder would load the on-disk file
    without verification. This test poisons the on-disk bytes for the
    helper to raise on execution — if the test passes (no exception),
    the in-memory verified bytes were served.
    """
    from checkov.common.checks.base_check_registry import BaseCheckRegistry

    # dir-A has the "check" that imports the helper.
    dir_a = tmp_path / "checks_a"
    dir_a.mkdir()
    (dir_a / "__init__.py").write_bytes(make_trailer(b"", priv_a))
    check_body = (
        b"import cross_dir_shared_helper\n"
        b"PROVIDER = cross_dir_shared_helper.PROVIDER_NAME\n"
    )
    (dir_a / "cross_dir_check.py").write_bytes(make_trailer(check_body, priv_a))

    # dir-B holds the helper. Sign it with the SAFE in-memory bytes,
    # then OVERWRITE the on-disk file with bytes that raise on exec.
    # Verification ran against the safe bytes (they live in the
    # in-memory allowlist); the on-disk bytes are now a tripwire.
    dir_b = tmp_path / "checks_b"
    dir_b.mkdir()
    (dir_b / "__init__.py").write_bytes(make_trailer(b"", priv_a))
    helper_path = dir_b / "cross_dir_shared_helper.py"
    safe_helper_bytes = b"PROVIDER_NAME = 'verified-helper'\n"
    helper_path.write_bytes(make_trailer(safe_helper_bytes, priv_a))

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    verify_and_register([str(dir_a), str(dir_b)], [str(key_path)])

    # AFTER verification registered the safe bytes, overwrite the disk
    # file with a tripwire. If the finder falls back to disk-load, this
    # raises and the test fails loudly.
    helper_path.write_bytes(
        b"raise RuntimeError('cross-dir transitive import fell back to disk-load; "
        b"M1 bypass is live')\n"
    )

    class _StubRegistry(BaseCheckRegistry):
        def extract_entity_details(self, entity):
            return ("", "", {})

    # Mimic the real runner loop: load each dir in turn through the
    # SAME registry. The bypass only manifests when the finder for the
    # current call doesn't know about the other dir's verified sources.
    registry = _StubRegistry(report_type="terraform")
    sys.modules.pop("cross_dir_check", None)
    sys.modules.pop("cross_dir_shared_helper", None)
    try:
        # Load dir-A first; the check it contains imports the helper
        # from dir-B during its own exec. If the bypass exists, the
        # tripwire on disk fires here.
        registry.load_external_checks(str(dir_a))
        registry.load_external_checks(str(dir_b))

        # The helper must have been served from the in-memory bytes.
        helper_mod = sys.modules.get("cross_dir_shared_helper")
        assert helper_mod is not None, (
            "the helper did not register at all — finder did not serve it"
        )
        assert helper_mod.PROVIDER_NAME == "verified-helper", (
            f"helper executed the WRONG bytes: PROVIDER_NAME="
            f"{helper_mod.PROVIDER_NAME!r}. The tripwire on disk should have "
            f"either fired (RuntimeError) or been bypassed by serving the "
            f"in-memory bytes; got disk bytes silently."
        )
        # And the check itself observed the helper's verified value.
        check_mod = sys.modules.get("cross_dir_check")
        assert check_mod is not None
        assert check_mod.PROVIDER == "verified-helper"
    finally:
        sys.modules.pop("cross_dir_check", None)
        sys.modules.pop("cross_dir_shared_helper", None)


# --------------------------------------------------------------------------
# 11. M2: load_public_keys catches ONLY the expected PEM-load failure modes.
#
# The original code did `except (MalformedPointError, ValueError, TypeError,
# Exception)` which collapses literally every Exception subclass to a
# misleading "unsupported key format" diagnostic, including unrelated
# RuntimeErrors from a misbehaving third-party hook. The fix narrows the
# tuple to the actual failure surface of ecdsa.from_pem (UnexpectedDER,
# binascii.Error, MalformedPointError, ValueError, TypeError). Anything
# outside that set must propagate so operators see the real root cause.
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("scenario_id", "pem_bytes"),
    [
        ("empty_bytes",        b""),
        ("garbage_non_pem",    b"this is not a pem"),
        ("only_header_footer", b"-----BEGIN PUBLIC KEY-----\n-----END PUBLIC KEY-----\n"),
        ("garbage_base64",     b"-----BEGIN PUBLIC KEY-----\nnot-base64-at-all\n-----END PUBLIC KEY-----\n"),
        # 60+ valid-base64 bytes that decode to a non-DER body.
        ("valid_b64_garbage_body",
         b"-----BEGIN PUBLIC KEY-----\n"
         b"aGVsbG8gd29ybGQgaGVsbG8gd29ybGQgaGVsbG8gd29ybGQgaGVsbG8gd29ybGQgaGVsbG8gd29ybGQ=\n"
         b"-----END PUBLIC KEY-----\n"),
        # Truncated DER body (length byte claims more than the buffer carries).
        ("truncated_der",
         b"-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQg==\n-----END PUBLIC KEY-----\n"),
    ],
)
def test_garbage_pem_inputs_still_collapse_to_unsupported_key_format(
    scenario_id: str, pem_bytes: bytes, tmp_path: Path,
):
    """Every legitimate "this isn't a usable P-256 SPKI" input must still
    surface as ``unsupported key format in <path>``.

    Pins the M2 narrowing: the new tuple covers UnexpectedDER (subclass
    of ValueError), binascii.Error, and the existing ValueError/TypeError
    fallbacks. If any of these inputs ever escapes the catch (i.e. the
    test would now raise the underlying library error instead of the
    customer-facing SignatureVerificationError), M2 was over-tightened.
    """
    pem_path = tmp_path / f"{scenario_id}.pem"
    pem_path.write_bytes(pem_bytes)

    with pytest.raises(SignatureVerificationError) as exc:
        load_public_keys([str(pem_path)])
    assert "unsupported key format" in str(exc.value).lower(), (
        f"scenario {scenario_id!r} did not produce the canonical "
        f"'unsupported key format' diagnostic; got {exc.value!r}"
    )


def test_load_public_keys_propagates_unexpected_exception_types(
    tmp_path: Path, monkeypatch,
):
    """An exception type OUTSIDE the M2 expected-error set propagates.

    Pins that the catch was narrowed correctly. If a future refactor
    re-broadens the tuple to ``Exception``, this test fails. Without
    this test, a regression that hides a genuine RuntimeError behind a
    misleading "unsupported key format" diagnostic would land silently
    and cost operators hours of debugging on unrelated root causes.
    """
    pem_path = tmp_path / "trigger.pem"
    pem_path.write_bytes(b"-----BEGIN PUBLIC KEY-----\nXXXX\n-----END PUBLIC KEY-----\n")

    sentinel = RuntimeError("simulated third-party hook explosion")

    def _exploding_from_pem(*_args, **_kwargs):
        raise sentinel

    from checkov.common.external_checks.verification import keys as keys_mod
    monkeypatch.setattr(keys_mod.VerifyingKey, "from_pem", staticmethod(_exploding_from_pem))

    with pytest.raises(RuntimeError) as raised:
        load_public_keys([str(pem_path)])
    assert raised.value is sentinel, (
        "the RuntimeError was swallowed and replaced with another exception; "
        "M2 narrowing has regressed back to a broad catch — see keys.py"
    )


# --------------------------------------------------------------------------
# 12. S1: log-file write failure surfaces a warning on stderr.
#
# The stderr message points the operator at ./checkov-verification-failures.log
# but if cwd is read-only (CI sandbox, read-only container) the write fails
# silently. The operator follows the breadcrumb and finds nothing. S1
# requires that we explicitly tell them the log couldn't be written.
# --------------------------------------------------------------------------


def test_failure_log_write_failure_warns_on_stderr(
    unsigned_dir: Path, key_a_pub_pem: bytes, tmp_path: Path,
):
    """When the failure log cannot be written, stderr gets an explicit
    warning instead of just silently dropping the file.
    """
    import io
    import contextlib
    from unittest.mock import patch
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

    captured_stderr = io.StringIO()
    # Patch open() to raise on the write-only log file path; all other
    # `open` calls (key file etc.) must pass through to the real builtin.
    real_open = open
    log_filename = "checkov-verification-failures.log"

    def _selective_open(path, *args, **kwargs):
        if isinstance(path, str) and log_filename in path:
            raise OSError("Read-only file system (simulated)")
        return real_open(path, *args, **kwargs)

    with patch("checkov.main.bc_integration") as bc, \
         patch("builtins.open", side_effect=_selective_open), \
         contextlib.redirect_stderr(captured_stderr):
        bc.sast_custom_policies = None
        prev_cwd = os.getcwd()
        os.chdir(str(tmp_path))
        try:
            with pytest.raises(SystemExit):
                instance.get_external_checks_dir()
        finally:
            os.chdir(prev_cwd)

    stderr_text = captured_stderr.getvalue()
    assert "could not write" in stderr_text, (
        "expected an explicit 'could not write ...' warning on stderr when "
        "the failure log cannot be written; got:\n" + stderr_text
    )
    assert log_filename in stderr_text, (
        "the warning should name the path that failed so the operator can "
        "diagnose (e.g. read-only mount, full disk)"
    )
