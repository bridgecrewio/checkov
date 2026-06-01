from __future__ import annotations

import logging
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


def _patch_git_getter(returns_path: Path):
    """Patch ``checkov.main.GitGetter`` so ``.get()`` returns ``returns_path``.

    Use as a context manager wrapping the call to ``get_external_checks_dir``.
    """
    class _StubGetter:
        def __init__(self, url: str) -> None:
            self.url = url

        def get(self) -> str:
            return str(returns_path)

    return patch("checkov.main.GitGetter", _StubGetter)


def _run_chokepoint(
    checkov: Checkov, clone_result: Path, caplog=None,
) -> "tuple[list[str] | SystemExit, str]":
    """Drive the chokepoint with a patched GitGetter; return ``(result, log_text)``.

    ``result`` is the returned dir list on success, or the ``SystemExit``
    on verification failure. ``log_text`` is captured via ``caplog`` if
    provided; otherwise an empty string.
    """
    log_capture = (
        caplog.at_level(logging.ERROR, logger="checkov.main")
        if caplog is not None
        else _noop_ctx()
    )
    # atexit.register inside main.py is harmless under test (the temp dir
    # is owned by the test's tmp_path), but mute it to keep test output clean.
    with patch("checkov.main.bc_integration") as bc, \
         patch("checkov.main.atexit"), \
         _patch_git_getter(clone_result), \
         log_capture:
        bc.sast_custom_policies = None
        try:
            result = checkov.get_external_checks_dir()
        except SystemExit as exc:
            return exc, (caplog.text if caplog is not None else "")
    return result, (caplog.text if caplog is not None else "")


import contextlib as _contextlib


@_contextlib.contextmanager
def _noop_ctx():
    yield


# --------------------------------------------------------------------------
# Happy path
# --------------------------------------------------------------------------


def test_git_no_key_skips_verification(valid_dir: Path, make_checkov):
    """``--external-checks-git`` without a public key → no verification at all."""
    checkov = make_checkov(
        external_checks_git=["https://example.invalid/repo.git"],
    )
    result, _ = _run_chokepoint(checkov, valid_dir)
    assert isinstance(result, list)
    assert result == [str(valid_dir)]
    assert is_verification_active() is False


def test_git_signed_clone_with_matching_key_verifies(
    valid_dir: Path, key_a_pub_pem: bytes, tmp_path: Path, make_checkov,
):
    """A signed git clone + matching key → verification succeeds, registry active."""
    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)

    checkov = make_checkov(
        external_checks_git=["https://example.invalid/repo.git"],
        external_checks_public_key=[str(key_path)],
    )
    result, _ = _run_chokepoint(checkov, valid_dir)
    assert isinstance(result, list)
    assert result == [str(valid_dir)]
    assert is_verification_active() is True


# --------------------------------------------------------------------------
# Rejection paths
# --------------------------------------------------------------------------


def test_git_unsigned_clone_with_key_exits_via_exit_run(
    unsigned_dir: Path, key_a_pub_pem: bytes, tmp_path: Path, make_checkov, caplog,
):
    """An unsigned git clone + key → exit_run() invoked, no scan.

    Routing through ``self.exit_run()`` is what gives ``--no-fail-on-crash``
    its documented contract — exit 0 with the failure still surfaced on
    stderr (via logging).
    """
    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)

    checkov = make_checkov(
        external_checks_git=["https://example.invalid/repo.git"],
        external_checks_public_key=[str(key_path)],
    )

    result, log_text = _run_chokepoint(checkov, unsigned_dir, caplog=caplog)

    assert isinstance(result, SystemExit)
    assert result.code == 2
    assert "External checks signature verification failed" in log_text
    assert is_verification_active() is False


def test_git_modified_clone_with_key_exits_2(
    mutated_dir: Path, key_a_pub_pem: bytes, tmp_path: Path, make_checkov, caplog,
):
    """A signed-then-mutated git clone + key → exit 2 + diagnostic logged."""
    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)

    checkov = make_checkov(
        external_checks_git=["https://example.invalid/repo.git"],
        external_checks_public_key=[str(key_path)],
    )

    result, log_text = _run_chokepoint(checkov, mutated_dir, caplog=caplog)

    assert isinstance(result, SystemExit)
    assert result.code == 2
    assert "External checks signature verification failed" in log_text


def test_git_unsigned_clone_with_key_and_no_fail_on_crash_exits_0(
    unsigned_dir: Path, key_a_pub_pem: bytes, tmp_path: Path, make_checkov, caplog,
):
    """Same as the unsigned-rejection test, but with ``--no-fail-on-crash``.

    Documents that the flag's "exit 0 instead of 2" contract applies to
    git-sourced verification failures exactly the same as to local-dir
    verification failures.
    """
    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)

    checkov = make_checkov(
        external_checks_git=["https://example.invalid/repo.git"],
        external_checks_public_key=[str(key_path)],
        no_fail_on_crash=True,
    )

    result, log_text = _run_chokepoint(checkov, unsigned_dir, caplog=caplog)

    assert isinstance(result, SystemExit)
    assert result.code == 0
    # Diagnostic surface is unchanged — only the exit code differs.
    assert "External checks signature verification failed" in log_text


# --------------------------------------------------------------------------
# Flag interaction
# --------------------------------------------------------------------------


def test_git_overrides_local_dir_when_both_are_set(
    valid_dir: Path, key_a_pub_pem: bytes, tmp_path: Path, make_checkov,
):
    """If both ``--external-checks-dir`` AND ``--external-checks-git`` are passed,
    the git clone REPLACES the local dir.

    Documents the current chokepoint behaviour at
    [`main.py:802-805`](checkov/checkov/main.py:802) — there is no CLI-level
    mutex enforcement, so this assignment matters. Verification then runs
    against the git clone path only.

    If a future change adds CLI-level mutex enforcement, this test should
    be updated to assert the CLI rejects the combination instead.
    """
    # The "local dir" is a throwaway sibling that should NOT be verified.
    decoy_dir = tmp_path / "decoy_local_dir_that_should_be_ignored"
    decoy_dir.mkdir()
    (decoy_dir / "__init__.py").write_text("")
    (decoy_dir / "should_not_be_loaded.py").write_text(
        "# unsigned decoy — must not appear in the verified allowlist\n"
    )

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)

    checkov = make_checkov(
        external_checks_dir=[str(decoy_dir)],
        external_checks_git=["https://example.invalid/repo.git"],
        external_checks_public_key=[str(key_path)],
    )
    # The "clone" returns the signed valid_dir, so verification should succeed.
    result, _ = _run_chokepoint(checkov, valid_dir)
    assert isinstance(result, list)
    # The returned list is the git clone path, NOT the decoy local dir.
    assert result == [str(valid_dir)]
    assert str(decoy_dir) not in result, (
        "the local --external-checks-dir argument should have been overwritten "
        "by the git clone result; the decoy dir leaked through"
    )
    assert is_verification_active() is True


# --------------------------------------------------------------------------
# Robustness: clone artefacts inside the temp dir
# --------------------------------------------------------------------------


def test_git_clone_with_pycache_in_repo_is_handled(
    tmp_path: Path, priv_a, key_a_pub_pem: bytes, make_trailer, make_checkov,
):
    """A git clone that happens to ship a ``__pycache__/`` (e.g. checked in by
    accident or left over from local CI) must be silently skipped by the
    walker — same behaviour as the local-dir case.
    """
    clone = tmp_path / "fake_clone"
    clone.mkdir()
    (clone / "__init__.py").write_bytes(make_trailer(b"", priv_a))
    body = b"# signed via git\nCHECK_ID = 'CKV_GIT_1'\n"
    (clone / "checked.py").write_bytes(make_trailer(body, priv_a))
    # And a pre-existing __pycache__/ with a stale .pyc — the walker
    # skips __pycache__ subdirs entirely.
    cache_dir = clone / "__pycache__"
    cache_dir.mkdir()
    (cache_dir / "stale.cpython-312.pyc").write_bytes(b"\x00fake bytecode")

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)

    checkov = make_checkov(
        external_checks_git=["https://example.invalid/repo.git"],
        external_checks_public_key=[str(key_path)],
    )
    result, _ = _run_chokepoint(checkov, clone)
    assert isinstance(result, list)
    assert is_verification_active() is True


# --------------------------------------------------------------------------
# Multiple --external-checks-git args
# --------------------------------------------------------------------------


def test_git_only_first_url_is_used(
    valid_dir: Path, key_a_pub_pem: bytes, tmp_path: Path, make_checkov,
):
    """``--external-checks-git`` is declared as ``action='append'`` but the
    chokepoint only consumes the first URL — confirm so future operators
    don't silently lose verification of the second/third URL.

    Pins the current behaviour at
    [`main.py:804`](checkov/checkov/main.py:804) — ``self.config.external_checks_git[0]``.
    """
    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)

    checkov = make_checkov(
        external_checks_git=[
            "https://example.invalid/first.git",
            "https://example.invalid/second.git",  # SILENTLY IGNORED today
        ],
        external_checks_public_key=[str(key_path)],
    )
    captured_urls: list[str] = []

    class _RecordingGetter:
        def __init__(self, url: str) -> None:
            captured_urls.append(url)

        def get(self) -> str:
            return str(valid_dir)

    with patch("checkov.main.GitGetter", _RecordingGetter), \
         patch("checkov.main.bc_integration") as bc, \
         patch("checkov.main.atexit"):
        bc.sast_custom_policies = None
        result = checkov.get_external_checks_dir()

    assert isinstance(result, list)
    assert captured_urls == ["https://example.invalid/first.git"], (
        "the chokepoint should consume only the first --external-checks-git URL; "
        f"got URLs={captured_urls!r}. If this fails, the chokepoint was changed to "
        "iterate all URLs — update the test, and also verify each URL's clone runs "
        "through verify_and_register."
    )


# --------------------------------------------------------------------------
# S4: TOCTOU regression — late mutation of git clone caught by loader escalation
# --------------------------------------------------------------------------


def test_late_modification_of_git_clone_is_caught_by_loader_escalation(
    valid_dir: Path, key_a_pub_pem: bytes, tmp_path: Path, make_checkov, stub_registry,
):
    """Closes the S4 disk-drift window: between ``verify_and_register`` (at
    the chokepoint) and ``load_external_checks`` (during the scan), the
    cloned git directory lives on disk and is mutable. A careless
    build-script artefact (or any unrelated process) dropping an extra
    ``.py`` into the cloned dir AFTER verification but BEFORE the loader
    walks it must NOT silently shrink/grow the verified check set — the
    loader's M1+S3 escalation must catch the divergence and raise
    ``SignatureVerificationError``.

    Mirrors the local-dir regression already pinned in
    ``test_verified_loader.test_load_external_checks_refuses_unverified_file``,
    but starts from the git-clone code path so the regression covers the
    full ``--external-checks-git`` lifecycle end-to-end. No production-code
    change is required if the existing M1+S3 fix is wired correctly.
    """
    from checkov.common.external_checks.verification import (
        SignatureVerificationError,
    )

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)

    checkov = make_checkov(
        external_checks_git=["https://example.invalid/repo.git"],
        external_checks_public_key=[str(key_path)],
    )

    # Chokepoint runs against the signed ``valid_dir`` (stand-in for the
    # post-clone temp dir GitGetter would have returned in production).
    result, _ = _run_chokepoint(checkov, valid_dir)
    assert isinstance(result, list)
    assert is_verification_active() is True

    # Simulate the TOCTOU window: drop an unverified file into the cloned
    # dir AFTER verify_and_register has populated the in-memory allowlist.
    # Bytes that would raise on exec — proves the loader never exec'd them
    # (the divergence is caught at the resolve step, before exec).
    evil = valid_dir / "evil.py"
    evil.write_bytes(b"raise RuntimeError('TOCTOU drop was executed')\n")

    registry = stub_registry

    # The loader resolves ``verified_sources`` from the in-memory registry
    # populated by the chokepoint, then walks the dir; ``evil.py`` is on
    # disk but absent from the allowlist → escalates.
    with pytest.raises(SignatureVerificationError) as exc:
        registry.load_external_checks(str(valid_dir.resolve()))

    assert "evil.py" in str(exc.value)
