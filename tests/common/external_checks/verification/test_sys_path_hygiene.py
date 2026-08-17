"""``sys.path`` hygiene for the verified external-checks load path.

The verified load path is fastidious about cleanup elsewhere — it
uninstalls the meta-path finder, restores ``sys.dont_write_bytecode``,
and removes failed modules from ``sys.modules``. ``sys.path`` was the
one exception: every walked subdirectory was ``insert(1, root)``-ed
and never removed.

This is the regression test that the verified path leaves
``sys.path`` byte-identical to its pre-call snapshot, just like the
other module-level state.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Callable

import pytest
from ecdsa import SigningKey

from checkov.common.external_checks.verification.sources_registry import (
    reset_for_tests,
    verify_and_register,
)


@pytest.fixture(autouse=True)
def _reset_registry():
    reset_for_tests()
    try:
        yield
    finally:
        reset_for_tests()


@pytest.fixture(autouse=True)
def _restore_sys_path():
    """Belt-and-braces: never let one test's leak bleed into the next."""
    snapshot = list(sys.path)
    try:
        yield
    finally:
        sys.path[:] = snapshot


def _build_nested_signed_dir(
    root: Path, priv: SigningKey, make_trailer: Callable[[bytes, SigningKey], bytes],
) -> Path:
    """Two-level signed tree: ``root/__init__.py``, ``root/sub/__init__.py``,
    ``root/sub/aws_check.py`` — every ``.py`` carries a valid trailer.

    The nested level is what reproduces the leak: the walker hits both
    ``root`` and ``root/sub`` and inserts both into ``sys.path``.
    """
    root.mkdir()
    (root / "__init__.py").write_bytes(make_trailer(b"", priv))
    sub = root / "sub"
    sub.mkdir()
    (sub / "__init__.py").write_bytes(make_trailer(b"", priv))
    (sub / "aws_check.py").write_bytes(
        make_trailer(b"# signed nested check\nCHECK_ID = 'CKV_T_SP'\n", priv)
    )
    return root


def test_verified_load_does_not_leak_sys_path(
    tmp_path: Path,
    priv_a: SigningKey,
    key_a_pub_pem: bytes,
    make_trailer: Callable[[bytes, SigningKey], bytes],
    stub_registry,
):
    """After ``load_external_checks()`` returns, ``sys.path`` is unchanged.

    The verified path already restores ``sys.dont_write_bytecode`` and
    uninstalls the meta-path finder; ``sys.path`` is the missing piece.
    Walked directories must not persist on ``sys.path`` for the rest of
    the process lifetime.
    """
    checks_root = _build_nested_signed_dir(
        tmp_path / "verified_checks", priv_a, make_trailer,
    )

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)

    # Register the directory through the same chokepoint the real code uses.
    verify_and_register([str(checks_root)], [str(key_path)])

    snapshot_before = list(sys.path)
    stub_registry.load_external_checks(str(checks_root))
    snapshot_after = list(sys.path)

    leaked = [p for p in snapshot_after if p not in snapshot_before]
    assert leaked == [], (
        f"verified load path leaked {len(leaked)} entries onto sys.path: "
        f"{leaked!r}. The verified path already restores "
        "sys.dont_write_bytecode and uninstalls the meta-path finder in a "
        "finally block; sys.path must be restored to its pre-call snapshot "
        "in the same finally block so external-check loading is hermetic."
    )
