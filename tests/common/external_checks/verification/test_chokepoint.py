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
from checkov.main import Checkov


@pytest.fixture(autouse=True)
def _reset_registry():
    reset_for_tests()
    try:
        yield
    finally:
        reset_for_tests()


def _make_checkov(
    *,
    external_checks_dir: "list[str] | None",
    external_checks_public_key: "list[str] | None" = None,
    external_checks_git: "list[str] | None" = None,
) -> Checkov:
    """Build a ``Checkov`` skeleton that exposes only what the chokepoint needs."""
    instance = Checkov.__new__(Checkov)
    instance.config = types.SimpleNamespace(  # type: ignore[attr-defined]
        external_checks_dir=external_checks_dir,
        external_checks_public_key=external_checks_public_key,
        external_checks_git=external_checks_git,
        no_fail_on_crash=False,
    )
    return instance


def test_no_keys_no_verification(valid_dir: Path):
    """No --external-checks-public-key → registry stays inactive."""
    checkov = _make_checkov(external_checks_dir=[str(valid_dir)])

    # Patch bc_integration.sast_custom_policies to None for isolation.
    with patch("checkov.main.bc_integration") as bc:
        bc.sast_custom_policies = None
        dirs = checkov.get_external_checks_dir()

    assert dirs == [str(valid_dir)]
    assert is_verification_active() is False


def test_no_external_checks_dir_skips_verification(
    key_a_pub_pem: bytes, tmp_path: Path,
):
    """Key configured but no dirs to verify → no-op, no error."""
    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)

    checkov = _make_checkov(
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
    valid_dir: Path, key_a_pub_pem: bytes, tmp_path: Path,
):
    """Happy path: signed dir + matching key → registry populated, dir returned."""
    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)

    checkov = _make_checkov(
        external_checks_dir=[str(valid_dir)],
        external_checks_public_key=[str(key_path)],
    )
    with patch("checkov.main.bc_integration") as bc:
        bc.sast_custom_policies = None
        dirs = checkov.get_external_checks_dir()

    assert dirs == [str(valid_dir)]
    assert is_verification_active() is True


def test_keys_plus_unsigned_dir_exits_via_exit_run(
    unsigned_dir: Path, key_a_pub_pem: bytes, tmp_path: Path,
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

    checkov = _make_checkov(
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
        with patch("checkov.main.bc_integration") as bc, pytest.raises(SystemExit) as raised:
            bc.sast_custom_policies = None
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
    valid_dir: Path, key_a_pub_pem: bytes, tmp_path: Path,
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

    checkov = _make_checkov(
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
