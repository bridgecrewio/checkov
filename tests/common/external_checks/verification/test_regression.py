from __future__ import annotations

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
#   * Flag OFF -> exit 2, diagnostic logged at ERROR level (stderr via logging).
#   * Flag ON  -> exit 0, SAME diagnostic logged.
# The flag changes ONLY the exit code, not the diagnostic surface.
# --------------------------------------------------------------------------


def _run_chokepoint(
    unsigned_dir: Path, key_a_pub_pem: bytes, tmp_path: Path,
    *, no_fail_on_crash: bool, caplog,
) -> "tuple[int, str]":
    """Run the chokepoint with a modified tree; return ``(exit_code, log_text)``."""
    import logging as _logging

    from checkov.main import Checkov

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)

    instance = Checkov.__new__(Checkov)
    instance.config = types.SimpleNamespace(  # type: ignore[attr-defined]
        external_checks_dir=[str(unsigned_dir)],
        external_checks_public_key=[str(key_path)],
        external_checks_git=None,
        no_fail_on_crash=no_fail_on_crash,
    )

    with patch("checkov.main.bc_integration") as bc, \
         caplog.at_level(_logging.ERROR, logger="checkov.main"):
        bc.sast_custom_policies = None
        prev_cwd = os.getcwd()
        os.chdir(str(tmp_path))
        try:
            with pytest.raises(SystemExit) as raised:
                instance.get_external_checks_dir()
        finally:
            os.chdir(prev_cwd)
    return raised.value.code, caplog.text


def test_verification_failure_without_no_fail_on_crash_exits_2(
    unsigned_dir: Path, key_a_pub_pem: bytes, tmp_path: Path, caplog,
):
    """Default flag state: verification failure exits 2."""
    code, log_text = _run_chokepoint(
        unsigned_dir, key_a_pub_pem, tmp_path,
        no_fail_on_crash=False, caplog=caplog,
    )
    assert code == 2
    assert "External checks signature verification failed" in log_text


def test_verification_failure_with_no_fail_on_crash_exits_0(
    unsigned_dir: Path, key_a_pub_pem: bytes, tmp_path: Path, caplog,
):
    """``--no-fail-on-crash`` aligns the security-failure exit code with the
    documented contract of the flag (``Return exit code 0 instead of 2``).

    The diagnostic surface — error message logged to stderr — is
    UNCHANGED. Only the exit code differs. Operators who need the pipeline
    to fail must either drop the flag or grep the stderr diagnostic.
    """
    code, log_text = _run_chokepoint(
        unsigned_dir, key_a_pub_pem, tmp_path,
        no_fail_on_crash=True, caplog=caplog,
    )
    assert code == 0, (
        "--no-fail-on-crash documents 'Return exit code 0 instead of 2'; "
        f"got {code!r}"
    )
    assert "External checks signature verification failed" in log_text


def test_exit_run_honours_no_fail_on_crash(tmp_path: Path):
    """Sanity: ``exit_run`` honours ``--no-fail-on-crash`` uniformly."""
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
    tmp_path: Path, priv_a, key_a_pub_pem: bytes, make_trailer, stub_registry,
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
    registry = stub_registry

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
# 4. Diagnostic truncation on huge failure lists keeps the logged message
#    readable; long lists are truncated with an "... and N more" hint.
# --------------------------------------------------------------------------


def test_diagnostic_truncated_on_huge_failure_list(
    tmp_path: Path, key_a_pub_pem: bytes, caplog,
):
    """A 100-bad-file failure logs ~20 inline lines plus a "... N more" hint."""
    import logging as _logging

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

    with patch("checkov.main.bc_integration") as bc, \
         caplog.at_level(_logging.ERROR, logger="checkov.main"):
        bc.sast_custom_policies = None
        prev_cwd = os.getcwd()
        os.chdir(str(tmp_path))
        try:
            with pytest.raises(SystemExit) as raised:
                instance.get_external_checks_dir()
        finally:
            os.chdir(prev_cwd)

    assert raised.value.code == 2
    log_text = caplog.text

    # Hard upper bound on inline failure lines (~20 visible + truncation hint).
    visible_failure_lines = [
        ln for ln in log_text.split("\n") if ln.strip().startswith("- missing signature:")
    ]
    assert len(visible_failure_lines) <= 25, (
        f"diagnostic logged {len(visible_failure_lines)} inline failure lines; "
        f"expected ~20 with a truncation hint"
    )
    assert "... and" in log_text and "more" in log_text, (
        "expected a 'and N more' truncation hint in the diagnostic"
    )


def test_diagnostic_not_truncated_when_failure_list_is_short(
    unsigned_dir: Path, key_a_pub_pem: bytes, tmp_path: Path, caplog,
):
    """A 1-bad-file failure logs the whole list inline, no truncation hint."""
    import logging as _logging

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

    with patch("checkov.main.bc_integration") as bc, \
         caplog.at_level(_logging.ERROR, logger="checkov.main"):
        bc.sast_custom_policies = None
        prev_cwd = os.getcwd()
        os.chdir(str(tmp_path))
        try:
            with pytest.raises(SystemExit):
                instance.get_external_checks_dir()
        finally:
            os.chdir(prev_cwd)

    assert "... and" not in caplog.text


# --------------------------------------------------------------------------
# 5. v1 scope pin: same-stem checks across subdirectories collide
#    deterministically (one wins by bare module name). Documented in the
#    customer-facing docs as a v1 limitation.
# --------------------------------------------------------------------------


def test_same_stem_checks_in_subdirectories_collide_deterministically(
    tmp_path: Path, priv_a, key_a_pub_pem: bytes, make_trailer, stub_registry,
):
    """Two ``helper.py`` files in different subdirectories collide on ``helper``.

    The exact winner is not part of the contract — the test only asserts
    that *one* of them wins deterministically and the other is shadowed.
    """
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

    registry = stub_registry

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
        b"\x00",   # NUL byte — not a valid hex character
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


def test_pyc_outside_pycache_is_silently_ignored(
    tmp_path: Path, priv_a, key_a_pub_pem: bytes, make_trailer,
):
    """A ``.pyc`` outside ``__pycache__/`` is silently ignored.

    Only ``.py`` files are loaded by the external-checks loader, so
    stray binary loadables anywhere in the tree are out of scope for
    trailer signing — they do not cause the scan to fail.
    """
    root = tmp_path / "loose_pyc"
    root.mkdir()
    (root / "__init__.py").write_bytes(make_trailer(b"", priv_a))
    (root / "check.py").write_bytes(make_trailer(b"# signed\n", priv_a))
    # A stray .pyc at top-level — NOT inside __pycache__.
    (root / "stray.pyc").write_bytes(b"\x00\x01\x02")

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])

    # Must not raise — .pyc is ignored regardless of location.
    verified = verify_external_checks_dirs([str(root)], keys)
    assert any(p.endswith("check.py") for p in verified)
    assert not any(p.endswith(".pyc") for p in verified)


def test_verified_load_does_not_create_pycache(
    tmp_path: Path, priv_a, key_a_pub_pem: bytes, make_trailer, stub_registry,
):
    """A successful verified load must not leave a ``__pycache__/`` behind.

    Pins the ``sys.dont_write_bytecode = True`` window so verified scans
    don't pollute the source tree with bytecode artefacts.
    """
    root = tmp_path / "fresh"
    root.mkdir()
    (root / "__init__.py").write_bytes(make_trailer(b"", priv_a))
    (root / "fresh_check.py").write_bytes(
        make_trailer(b"# signed\nID = 'CKV_FRESH'\n", priv_a)
    )

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    verify_and_register([str(root)], [str(key_path)])

    sys.modules.pop("fresh_check", None)
    try:
        stub_registry.load_external_checks(str(root))
    finally:
        sys.modules.pop("fresh_check", None)

    pycache = root / "__pycache__"
    assert not pycache.exists(), (
        f"verified load created a __pycache__ directory; should have been "
        f"prevented by sys.dont_write_bytecode. Contents: "
        f"{list(pycache.iterdir()) if pycache.exists() else 'N/A'}"
    )


def test_dont_write_bytecode_state_restored_after_load(
    tmp_path: Path, priv_a, key_a_pub_pem: bytes, make_trailer, stub_registry_cls,
):
    """``sys.dont_write_bytecode`` returns to its pre-call value after load.

    The verified-load window must not permanently silence bytecode
    writing for the rest of the process.
    """
    root = tmp_path / "restore_test"
    root.mkdir()
    (root / "__init__.py").write_bytes(make_trailer(b"", priv_a))
    (root / "check.py").write_bytes(make_trailer(b"# signed\n", priv_a))

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    verify_and_register([str(root)], [str(key_path)])

    # Exercise both starting values to confirm the restore is faithful.
    for initial in (False, True):
        previous = sys.dont_write_bytecode
        sys.dont_write_bytecode = initial
        sys.modules.pop("check", None)
        try:
            stub_registry_cls(report_type="terraform").load_external_checks(str(root))
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
# This is the integrity invariant: while ANY verified load is in
# flight, EVERY allowlisted .py — regardless of which dir registered
# it — must be served from the in-memory verified bytes. Otherwise a
# modified on-disk helper.py in dir-B could leak into the process
# via a transitive `import helper` from a verified check in dir-A.
# The bytes the verifier hashed must be the bytes the interpreter
# executes, transitively.
# --------------------------------------------------------------------------


def test_cross_dir_transitive_import_serves_in_memory_bytes(
    tmp_path: Path, priv_a, key_a_pub_pem: bytes, make_trailer, stub_registry,
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

    # Mimic the real runner loop: load each dir in turn through the
    # SAME registry. The bypass only manifests when the finder for the
    # current call doesn't know about the other dir's verified sources.
    registry = stub_registry
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
        ("empty_bytes", b""),
        ("garbage_non_pem", b"this is not a pem"),
        ("only_header_footer", b"-----BEGIN PUBLIC KEY-----\n-----END PUBLIC KEY-----\n"),
        ("garbage_base64", b"-----BEGIN PUBLIC KEY-----\nnot-base64-at-all\n-----END PUBLIC KEY-----\n"),
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


def test_verify_against_keys_propagates_unexpected_exception_types():
    """An exception type OUTSIDE the verify-side expected-error set propagates.

    Mirrors ``test_load_public_keys_propagates_unexpected_exception_types``
    at the M2-sibling layer in ``verifier._verify_against_keys``. The
    blanket ``except Exception: continue`` was deliberately narrowed
    to ``(BadSignatureError, UnexpectedDER, MalformedPointError,
    ValueError)`` so that non-crypto faults from a misbehaving key
    provider (HSM timeout, KMS unavailable, hardware-token
    disconnected, exhausted entropy pool) surface with their real
    root cause instead of being collapsed to ``UNKNOWN_KEY`` and a
    misleading "signature verification failed" diagnostic.
    """
    from unittest.mock import MagicMock
    from checkov.common.external_checks.verification import verify_bytes
    from checkov.common.external_checks.verification.keys import (
        VerificationKey,
    )

    # We need a properly-shaped file (passes the well-formedness checks)
    # so execution reaches _verify_against_keys. Use the conftest
    # fixtures via direct construction here to keep the test
    # self-contained — no signing needed because we control the key.
    # A 71-byte DER-shaped blob passes the strict-DER + range check.
    body = b"def check():\n    return 'ok'\n"
    # Build a plausible signed file: real body + a well-formed trailer.
    # Sign with an actual key so well-formedness passes, then point
    # verify_bytes at a MOCK key that raises on .verify().
    from ecdsa import NIST256p, SigningKey
    from ecdsa.util import sigencode_der
    import hashlib
    priv = SigningKey.generate(curve=NIST256p)
    sig_der = priv.sign_deterministic(
        body, hashfunc=hashlib.sha256, sigencode=sigencode_der,
    )
    file_bytes = body + b"# checkov-digest: " + sig_der.hex().encode("ascii") + b"\n"

    mock_public_key = MagicMock()
    mock_public_key.verify.side_effect = RuntimeError("simulated provider failure")
    failing_key = VerificationKey(
        public_key=mock_public_key,
        fingerprint_hex="deadbeef" * 8,
        source_path="/fake/kms/key.pem",
    )

    with pytest.raises(RuntimeError, match="simulated provider failure"):
        verify_bytes(file_bytes, [failing_key])

    assert mock_public_key.verify.call_count == 1, (
        "precondition: verify_bytes must reach _verify_against_keys "
        "(well-formedness check should have passed)"
    )


# --------------------------------------------------------------------------
# 12. T2: `cryptography` library is NOT in the import graph.
#
# The migration off ``cryptography`` to ``ecdsa`` is a deliberate
# dependency reduction. A future PR that re-introduces a transitive
# ``cryptography`` import (e.g. via a sibling util that gets pulled in
# by the verification package) would silently revive the old dep.
# --------------------------------------------------------------------------


def test_verification_package_does_not_import_cryptography():
    """Pin the dep migration: no transitive ``cryptography`` import via
    the verification surface."""
    import sys
    from checkov.common.external_checks import verification  # noqa: F401

    cryptography_modules = [m for m in sys.modules if m == "cryptography" or m.startswith("cryptography.")]
    assert not cryptography_modules, (
        f"verification package transitively imported the ``cryptography`` "
        f"library via: {cryptography_modules}. The migration to ``ecdsa`` "
        f"is supposed to drop this dep — investigate which import re-added it."
    )


# --------------------------------------------------------------------------
# 13. T3: property-style ~100 random bodies signed-then-verified.
#
# Catches edge cases in DER length variance (leading-zero stripping in
# ``r``/``s`` changes the signature length), trailer-length-guard
# interactions, and round-trip integrity for arbitrary content.
# --------------------------------------------------------------------------


def test_random_bodies_round_trip(
    tmp_path: Path, priv_a, key_a_pub_pem: bytes, make_trailer,
):
    """100 random bodies of varying sizes all sign-and-verify cleanly."""
    import random
    random.seed(0xC0FFEE)  # determinism across CI runs

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])

    for i in range(100):
        size = random.randint(0, 2048)
        # Always end the body in \n — the trailer parser requires the
        # signed payload to be \n-terminated. (Empty body is allowed.)
        body = (os.urandom(size) if size else b"") + b"\n"
        target = tmp_path / f"r_{i:03d}.py"
        target.write_bytes(make_trailer(body, priv_a))
        result, signed = verify_file(str(target), keys)
        assert result == VerificationResult.OK, (
            f"random body #{i} (size={size}) failed verification with {result!r}"
        )
        assert signed == body, (
            f"random body #{i}: verifier returned different bytes than the "
            f"original payload — round-trip integrity is broken"
        )


# --------------------------------------------------------------------------
# 14. T4: unverified default path queries the registry exactly once per
#         directory and (when verification is inactive) gets back ``None``.
#
# Spy on ``get_verified_sources_for_directory``. The contract is
# documented as "consulted, returns None when inactive" — this pins it
# so a refactor that bypasses the registry (or, worse, mutates it as
# a side effect) fails fast.
# --------------------------------------------------------------------------


def test_unverified_path_consults_registry_once_per_directory(
    tmp_path, monkeypatch, stub_registry,
):
    """Unverified disk-load path queries the registry once per call and gets None."""
    from checkov.common.checks import base_check_registry as mod

    checks_dir = tmp_path / "unverified"
    checks_dir.mkdir()
    (checks_dir / "__init__.py").write_bytes(b"")
    (checks_dir / "check.py").write_bytes(b"X = 1\n")

    calls: list[str] = []

    def _spy(directory: str):
        calls.append(directory)
        return None  # mimic inactive-registry contract

    monkeypatch.setattr(mod, "get_verified_sources_for_directory", _spy)

    stub_registry.load_external_checks(str(checks_dir))

    assert calls == [str(checks_dir).replace("/", os.sep)] or calls == [str(checks_dir)], (
        f"expected exactly one registry consultation for the loaded directory; "
        f"got {calls}"
    )


# --------------------------------------------------------------------------
# 15. T6: trailer line + \n + arbitrary-looking junk line + \n.
#
# A future "permissive parser" change could silently make
# ``trailer + \n + commented-code\n`` verify against the trailer. The
# current parser only checks the LAST \n-terminated line; assert this
# explicitly.
# --------------------------------------------------------------------------


def test_trailer_followed_by_junk_line_is_rejected(
    tmp_path: Path, priv_a, key_a_pub_pem: bytes, make_trailer,
):
    """``signed-file + \\nJUNK\\n`` → NO_SIGNATURE.

    The trailer is no longer the last line, so the parser must not
    treat it as the trailer. The "JUNK" line is the last line and it
    doesn't start with the trailer prefix → no trailer at all.
    """
    body = b"def check():\n    pass\n"
    signed = make_trailer(body, priv_a)
    target = tmp_path / "junked.py"
    target.write_bytes(signed + b"# innocent-looking trailing comment\n")

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])

    result, _ = verify_file(str(target), keys)
    assert result == VerificationResult.NO_SIGNATURE, (
        f"a trailer line followed by another \\n-terminated line was "
        f"silently accepted; expected NO_SIGNATURE, got {result!r}. "
        f"The parser's last-line-only invariant has regressed."
    )


# --------------------------------------------------------------------------
# 16. N2: realistic doc-string body with blank lines AND a literal
#         ``# checkov-digest:`` prefix mid-file is signed and verified
#         cleanly. Pins the "only the last line counts" invariant against
#         a body that closely mimics customer-facing doc examples.
# --------------------------------------------------------------------------


def test_doc_style_body_with_internal_trailer_prefix_round_trips(
    tmp_path: Path, priv_a, key_a_pub_pem: bytes, make_trailer,
):
    """A signed file whose body contains blank lines AND a literal
    ``# checkov-digest:`` line (e.g. embedded as a docstring example)
    must verify cleanly. Realistic shape of customer documentation."""
    body = (
        b'"""Example custom check.\n'
        b"\n"
        b"Signing recipe::\n"
        b"\n"
        b"    openssl dgst -sha256 -sign priv.pem check.py | xxd -p -c 256\n"
        b"    # checkov-digest: <hex>  <-- this is just doc text, not a trailer\n"
        b'"""\n'
        b"\n"
        b"def check():\n"
        b"    return True\n"
    )
    target = tmp_path / "doc_example.py"
    target.write_bytes(make_trailer(body, priv_a))

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])

    result, signed = verify_file(str(target), keys)
    assert result == VerificationResult.OK
    assert signed == body


# --------------------------------------------------------------------------
# 17. Verify-then-load disk-drift enforcement (M1 / S3).
#
# Between ``verify_and_register`` (chokepoint) and ``load_external_checks``
# (during scan) the on-disk file set can diverge from the in-memory
# allowlist — rename, late-added unverified file, ``git stash pop``
# during the scan, or a writable temp directory mutated by an
# unrelated process. The pre-fix loader handled both branches with a
# per-file ERROR log line and ``continue``'d, leaving the scan running
# with a silently-degraded check set. The fix collects every refused
# path and raises ``SignatureVerificationError`` at the end of the
# walk so the chokepoint's exit handler can route the failure through
# ``_report_verification_failure_and_exit`` and exit 2 (or 0 under
# ``--no-fail-on-crash``).
# --------------------------------------------------------------------------


def test_loader_escalates_when_verified_file_renamed_after_register(
    tmp_path: Path, priv_a, key_a_pub_pem: bytes, make_trailer, stub_registry,
):
    """A verified file renamed AFTER registration causes the loader to escalate.

    Pre-fix the loader only logged ERROR and continued, leaving the
    scan running with the renamed file silently absent from the
    verified check set. The fix raises ``SignatureVerificationError``
    naming the offending path so the operator sees a hard failure
    instead of a silently-shrunken allowlist.
    """
    root = tmp_path / "checks"
    root.mkdir()
    (root / "__init__.py").write_bytes(make_trailer(b"", priv_a))
    body = b"# signed\nCHECK_ID = 'CKV_T_M1'\n"
    (root / "aws_check.py").write_bytes(make_trailer(body, priv_a))

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)

    verify_and_register([str(root)], [str(key_path)])
    assert is_verification_active() is True

    # Rename the verified file AFTER registration. The registry still
    # has the ORIGINAL path; the on-disk name no longer matches.
    (root / "aws_check.py").rename(root / "aws_check_RENAMED.py")

    # Make sure no stale module is lingering from prior tests.
    sys.modules.pop("aws_check", None)
    sys.modules.pop("aws_check_RENAMED", None)

    registry = stub_registry
    with pytest.raises(SignatureVerificationError) as exc:
        registry.load_external_checks(str(root))

    assert "aws_check_RENAMED.py" in str(exc.value), (
        f"escalation should identify the offending file; got: {exc.value!r}"
    )


def test_loader_escalates_on_unverified_file_dropped_after_register(
    tmp_path: Path, priv_a, key_a_pub_pem: bytes, make_trailer, stub_registry,
):
    """An unverified ``.py`` appearing after register causes the loader to escalate.

    Models post-registration drift — accidental (``git stash pop``,
    build-script artefact) or environmental (writable container,
    shared CI runner with disk access during the scan). The pre-fix
    loader logged ERROR and proceeded; the fix collects every refused
    path and raises ``SignatureVerificationError`` so the chokepoint
    handles the failure uniformly.

    Sanity-checks the existing safety guarantee too: the bytes are
    never exec'd.
    """
    root = tmp_path / "checks"
    root.mkdir()
    (root / "__init__.py").write_bytes(make_trailer(b"", priv_a))
    (root / "good.py").write_bytes(
        make_trailer(b"# signed\nCHECK_ID = 'CKV_T_S3'\n", priv_a)
    )

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)

    verify_and_register([str(root)], [str(key_path)])
    assert is_verification_active() is True

    # Drop an unverified evil.py AFTER registration.
    (root / "evil.py").write_bytes(b"raise RuntimeError('this should not exec')\n")

    sys.modules.pop("evil", None)
    sys.modules.pop("good", None)

    registry = stub_registry
    with pytest.raises(SignatureVerificationError) as exc:
        registry.load_external_checks(str(root))

    assert "evil.py" in str(exc.value), (
        f"escalation should identify evil.py; got: {exc.value!r}"
    )
    # Sanity: the existing "bytes never exec" guarantee still holds.
    assert "evil" not in sys.modules, (
        "evil.py was exec'd despite missing from allowlist — that would "
        "be a critical-severity bypass, not just a TOCTOU escalation gap"
    )
