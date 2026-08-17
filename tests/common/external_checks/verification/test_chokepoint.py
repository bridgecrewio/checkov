"""Chokepoint tests for ``Checkov.get_external_checks_dir``.

Bypasses ``Checkov.__init__`` (which runs heavy ``parse_config`` setup)
by constructing instances via ``__new__`` and stubbing ``config`` and
``exit_run`` to the minimum the method needs. This keeps the test
focused on the verification chokepoint behaviour:

* No key configured → today's behaviour (no verification, no registry).
* Key configured + signed dir → verification succeeds, registry active.
* Key configured + unsigned/modified dir → exit_run() invoked, no scan.
* Platform-supplied ``sast_custom_policies`` is appended **after**
  verification and is not sent through it.
"""
from __future__ import annotations

import types
from pathlib import Path
from unittest.mock import patch

import pytest

from checkov.common.external_checks.verification.sources_registry import (
    is_verification_active,
    reset_for_tests,
)


@pytest.fixture(autouse=True)
def _reset_registry():
    reset_for_tests()
    try:
        yield
    finally:
        reset_for_tests()


def test_no_keys_no_verification(valid_dir: Path, make_checkov):
    """No --external-checks-public-key → registry stays inactive."""
    checkov = make_checkov(external_checks_dir=[str(valid_dir)])

    # Patch bc_integration.sast_custom_policies to None for isolation.
    with patch("checkov.main.bc_integration") as bc:
        bc.sast_custom_policies = None
        dirs = checkov.get_external_checks_dir()

    assert dirs == [str(valid_dir)]
    assert is_verification_active() is False


def test_no_external_checks_dir_skips_verification(
    key_a_pub_pem: bytes, tmp_path: Path, make_checkov,
):
    """Key configured but no dirs to verify → no-op, no error."""
    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)

    checkov = make_checkov(
        external_checks_dir=None,
        external_checks_public_key=[str(key_path)],
    )
    with patch("checkov.main.bc_integration") as bc:
        bc.sast_custom_policies = None
        dirs = checkov.get_external_checks_dir()

    # No user-supplied dirs and no platform dir → empty list-like (None or []).
    assert not dirs
    assert is_verification_active() is False


def test_keys_plus_signed_dir_activates_registry(
    valid_dir: Path, key_a_pub_pem: bytes, tmp_path: Path, make_checkov,
):
    """Happy path: signed dir + matching key → registry populated, dir returned."""
    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)

    checkov = make_checkov(
        external_checks_dir=[str(valid_dir)],
        external_checks_public_key=[str(key_path)],
    )
    with patch("checkov.main.bc_integration") as bc:
        bc.sast_custom_policies = None
        dirs = checkov.get_external_checks_dir()

    assert dirs == [str(valid_dir)]
    assert is_verification_active() is True


def test_keys_plus_unsigned_dir_exits_via_exit_run(
    unsigned_dir: Path, key_a_pub_pem: bytes, tmp_path: Path, make_checkov,
):
    """Verification failure routes the exit through ``self.exit_run()``.

    ``exit_run()`` honours ``--no-fail-on-crash`` — the documented contract
    of that flag is to "Return exit code 0 instead of 2". The chokepoint
    therefore reports the failure (stderr + log file), then delegates the
    actual ``exit()`` call to ``self.exit_run()`` so the flag's contract
    is preserved end-to-end. Verified here by stubbing ``exit_run`` to a
    sentinel and asserting it fires.
    """
    import os
    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)

    checkov = make_checkov(
        external_checks_dir=[str(unsigned_dir)],
        external_checks_public_key=[str(key_path)],
    )

    exit_run_called: list[bool] = []

    def _fake_exit_run(self):
        exit_run_called.append(True)
        # Mirror the real exit_run's terminating behaviour so the caller
        # doesn't accidentally proceed past the failure point.
        raise SystemExit(2 if not self.config.no_fail_on_crash else 0)

    checkov.exit_run = types.MethodType(_fake_exit_run, checkov)  # type: ignore[attr-defined]

    prev_cwd = os.getcwd()
    os.chdir(str(tmp_path))
    try:
        with patch("checkov.main.bc_integration") as bc:
            bc.sast_custom_policies = None
            with pytest.raises(SystemExit) as raised:
                checkov.get_external_checks_dir()
    finally:
        os.chdir(prev_cwd)

    assert exit_run_called, (
        "verification failure must delegate exit to self.exit_run() so the "
        "--no-fail-on-crash contract is preserved; got direct sys.exit instead"
    )
    assert raised.value.code == 2, (
        f"with --no-fail-on-crash unset, exit must be 2; got {raised.value.code!r}"
    )
    assert is_verification_active() is False


def test_platform_policies_appended_after_verification(
    valid_dir: Path, key_a_pub_pem: bytes, tmp_path: Path, make_checkov,
):
    """sast_custom_policies dir is appended after verification.

    The platform-supplied dir must NOT pass through verify_and_register
    — it reaches Checkov through a different trust boundary (the
    integration's TLS-authenticated fetch) and is not part of the
    trailer-signing scope.
    """
    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)

    # Make a platform-style dir that would fail verification if mistakenly
    # included — contains an unsigned .py file.
    platform_dir = tmp_path / "platform_policies"
    platform_dir.mkdir()
    (platform_dir / "unsigned_platform.py").write_bytes(b"# unsigned\n")

    checkov = make_checkov(
        external_checks_dir=[str(valid_dir)],
        external_checks_public_key=[str(key_path)],
    )

    with patch("checkov.main.bc_integration") as bc:
        bc.sast_custom_policies = str(platform_dir)
        dirs = checkov.get_external_checks_dir()

    assert str(valid_dir) in dirs
    assert str(platform_dir) in dirs
    assert dirs.index(str(valid_dir)) < dirs.index(str(platform_dir))
    # And critically — verification did NOT raise on the platform dir.
    assert is_verification_active() is True


def test_cli_flag_is_registered_in_parser():
    """Smoke test: --external-checks-public-key parses with default None."""
    from checkov.common.util.ext_argument_parser import ExtArgumentParser

    parser = ExtArgumentParser(description="test")
    parser.add_parser_args()
    cfg = parser.parse_args([])
    assert cfg.external_checks_public_key is None

    cfg2 = parser.parse_args(
        ["--external-checks-public-key", "/tmp/a.pem",
         "--external-checks-public-key", "/tmp/b.pem"]
    )
    assert cfg2.external_checks_public_key == ["/tmp/a.pem", "/tmp/b.pem"]


def test_help_text_documents_no_fail_on_crash_override():
    """``--external-checks-public-key`` help mentions the ``--no-fail-on-crash`` override.

    Pins S5: the help text must accurately describe the runtime
    behaviour. The flag changes the exit code from 2 to 0 on
    verification failure (the documented contract of
    ``--no-fail-on-crash`` is "Return exit code 0 instead of 2", and
    verification failures honour that contract — see
    ``test_verification_failure_with_no_fail_on_crash_exits_0`` in
    ``test_regression.py``). The help text must mention this so
    operators see one source of truth, not a docs-vs-runtime drift.
    """
    from checkov.common.util.ext_argument_parser import ExtArgumentParser

    parser = ExtArgumentParser(description="test")
    parser.add_parser_args()

    action = next(
        (a for a in parser._actions if "--external-checks-public-key" in (a.option_strings or [])),
        None,
    )
    assert action is not None, (
        "could not find --external-checks-public-key action on the parser"
    )
    help_text = action.help or ""

    # The baseline exit code is still 2 — the help must keep saying so.
    assert "exit with code 2" in help_text, (
        f"help text must still mention the default 'exit with code 2'; "
        f"got: {help_text!r}"
    )
    # AND it must mention the --no-fail-on-crash override.
    assert "--no-fail-on-crash" in help_text, (
        f"help text must mention the --no-fail-on-crash override so "
        f"operators see one source of truth; got: {help_text!r}"
    )
