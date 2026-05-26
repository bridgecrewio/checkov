"""Tests for the in-memory verified-sources loader and meta-path finder.

Covers Phase 2 of the Option-B plan:

* Direct load via ``load_verified_sources_into_module`` execs the
  in-memory bytes, not the on-disk file (TOCTOU closure for direct
  loads).
* ``VerifiedSourcesFinder``, while installed, serves an ``import``
  request from the in-memory map (TOCTOU closure for transitive imports
  like ``import _helper`` from inside a verified check).
* ``BaseCheckRegistry.load_external_checks`` with ``verified_sources``
  refuses any on-disk ``.py`` file that is absent from the allowlist.
* The finder is fully cleaned up from ``sys.meta_path`` after
  ``load_external_checks`` returns — no leakage into the rest of the
  Python program.
* The legacy disk-load path (``verified_sources=None``) is byte-for-byte
  unchanged.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

from checkov.common.external_checks.verification.verified_loader import (
    VerifiedSourcesFinder,
    install_finder,
    load_verified_sources_into_module,
    uninstall_finder,
)


@pytest.fixture(autouse=True)
def _restore_sys_state():
    """Snapshot+restore sys.modules / sys.meta_path / sys.path around each test.

    Without this, a failing test could leave the meta-path finder
    installed and break the rest of the suite, or leave a half-loaded
    module in ``sys.modules`` that masks a real import error in the
    next test.
    """
    saved_modules = set(sys.modules.keys())
    saved_meta_path = list(sys.meta_path)
    saved_path = list(sys.path)
    try:
        yield
    finally:
        for added in set(sys.modules.keys()) - saved_modules:
            sys.modules.pop(added, None)
        sys.meta_path[:] = saved_meta_path
        sys.path[:] = saved_path


def test_load_verified_sources_into_module_execs_in_memory_bytes(tmp_path: Path):
    """Bytes argument is what's executed, even when the disk file differs."""
    on_disk = tmp_path / "victim.py"
    on_disk.write_bytes(b"ATTACKER = 'pwned'\n")
    safe_bytes = b"ATTACKER = 'safe'\nFLAG = 42\n"

    module = load_verified_sources_into_module(
        "victim_test_module_in_memory", str(on_disk), safe_bytes,
    )

    assert module.ATTACKER == "safe"  # in-memory bytes won
    assert module.FLAG == 42
    assert module.__file__ == str(on_disk)


def test_load_verified_sources_into_module_cleans_up_on_failure(tmp_path: Path):
    """A SyntaxError in the bytes leaves no half-loaded module behind."""
    on_disk = tmp_path / "broken.py"
    on_disk.write_bytes(b"# empty\n")

    with pytest.raises(SyntaxError):
        load_verified_sources_into_module(
            "victim_test_module_broken",
            str(on_disk),
            b"def broken(:\n",  # SyntaxError
        )

    assert "victim_test_module_broken" not in sys.modules


def test_finder_resolves_imports_from_in_memory_map(tmp_path: Path):
    """A normal ``import`` call goes through the finder when active."""
    on_disk = tmp_path / "trojan_helper.py"
    on_disk.write_bytes(b"raise RuntimeError('disk path was executed')\n")
    safe_bytes = b"VALUE = 'from-map'\n"

    finder = install_finder(
        {str(on_disk): safe_bytes},
        [str(tmp_path)],
    )
    try:
        module_name = "trojan_helper_test_module_in_memory"
        # The finder maps the import name 'trojan_helper' (via filename
        # 'trojan_helper.py') to the in-memory bytes; we use a uniquified
        # alias to avoid colliding with another test's sys.modules entry.
        import importlib
        spec = finder.find_spec("trojan_helper")
        assert spec is not None
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        assert module.VALUE == "from-map"  # in-memory bytes, not disk
    finally:
        uninstall_finder(finder)


def test_finder_returns_none_for_unknown_names(tmp_path: Path):
    """Unrecognised import names fall through to the next finder."""
    finder = VerifiedSourcesFinder({}, [str(tmp_path)])
    assert finder.find_spec("os") is None
    assert finder.find_spec("no_such_module_anywhere") is None
    assert finder.find_spec("pkg.submodule") is None  # dotted names ignored


def test_finder_is_removed_from_sys_meta_path_after_uninstall(tmp_path: Path):
    """install_finder + uninstall_finder leaves sys.meta_path as it was."""
    before = list(sys.meta_path)
    finder = install_finder({}, [str(tmp_path)])
    assert finder in sys.meta_path
    uninstall_finder(finder)
    assert finder not in sys.meta_path
    assert sys.meta_path == before


def test_uninstall_finder_is_idempotent(tmp_path: Path):
    """Calling uninstall twice does not raise."""
    finder = install_finder({}, [str(tmp_path)])
    uninstall_finder(finder)
    uninstall_finder(finder)  # second call must be a no-op


def test_load_external_checks_with_verified_sources_runs_in_memory(
    tmp_path: Path, capsys,
):
    """The registry loader execs the allowlist bytes, ignoring disk content."""
    from checkov.common.checks.base_check_registry import BaseCheckRegistry

    checks_dir = tmp_path / "checks"
    checks_dir.mkdir()
    (checks_dir / "__init__.py").write_bytes(b"")
    on_disk_check = checks_dir / "verified_check.py"
    on_disk_check.write_bytes(b"print('FROM_DISK')\n")  # would be visible if exec'd
    safe_bytes = b"print('FROM_MEMORY')\n"

    verified_sources = {
        str(on_disk_check.resolve()): safe_bytes,
    }

    # Need a concrete subclass; the abstract method isn't called in this path.
    class _StubRegistry(BaseCheckRegistry):
        def extract_entity_details(self, entity):
            return ("", "", {})

    registry = _StubRegistry(report_type="terraform")
    registry.load_external_checks(
        str(checks_dir.resolve()), verified_sources=verified_sources,
    )

    captured = capsys.readouterr()
    assert "FROM_MEMORY" in captured.out
    assert "FROM_DISK" not in captured.out


def test_load_external_checks_refuses_unverified_file(
    tmp_path: Path, caplog,
):
    """A .py file present on disk but absent from verified_sources is skipped."""
    import logging
    from checkov.common.checks.base_check_registry import BaseCheckRegistry

    checks_dir = tmp_path / "checks"
    checks_dir.mkdir()
    (checks_dir / "__init__.py").write_bytes(b"")
    drop_in = checks_dir / "unverified_drop_in.py"
    # Bytes that would *raise* if executed — proves the loader did not exec.
    drop_in.write_bytes(b"raise RuntimeError('unverified file was executed')\n")

    class _StubRegistry(BaseCheckRegistry):
        def extract_entity_details(self, entity):
            return ("", "", {})

    registry = _StubRegistry(report_type="terraform")

    with caplog.at_level(logging.ERROR):
        registry.load_external_checks(
            str(checks_dir.resolve()),
            verified_sources={},  # empty allowlist → every .py is unverified
        )

    # Test passes by *not* raising. The error log line is a UX nicety.
    assert any(
        "Refusing to load unverified external check" in record.message
        for record in caplog.records
    )


def test_load_external_checks_cleans_up_finder(tmp_path: Path):
    """sys.meta_path returns to its pre-call state once load returns."""
    from checkov.common.checks.base_check_registry import BaseCheckRegistry

    checks_dir = tmp_path / "checks"
    checks_dir.mkdir()
    (checks_dir / "__init__.py").write_bytes(b"")
    chk = checks_dir / "simple.py"
    chk.write_bytes(b"X = 1\n")

    class _StubRegistry(BaseCheckRegistry):
        def extract_entity_details(self, entity):
            return ("", "", {})

    registry = _StubRegistry(report_type="terraform")
    before = list(sys.meta_path)
    registry.load_external_checks(
        str(checks_dir.resolve()),
        verified_sources={str(chk.resolve()): b"X = 1\n"},
    )
    after = list(sys.meta_path)

    # No VerifiedSourcesFinder may remain on sys.meta_path.
    assert not any(isinstance(f, VerifiedSourcesFinder) for f in after)
    # And the path stack must be unchanged in identity-of-finders too.
    assert len(after) == len(before)


def test_legacy_load_external_checks_unchanged_when_no_verified_sources(
    tmp_path: Path, capsys,
):
    """Default behaviour (no verified_sources) execs from disk as before."""
    from checkov.common.checks.base_check_registry import BaseCheckRegistry

    checks_dir = tmp_path / "checks"
    checks_dir.mkdir()
    (checks_dir / "__init__.py").write_bytes(b"")
    chk = checks_dir / "legacy_check.py"
    chk.write_bytes(b"print('LEGACY_DISK_LOAD')\n")

    class _StubRegistry(BaseCheckRegistry):
        def extract_entity_details(self, entity):
            return ("", "", {})

    registry = _StubRegistry(report_type="terraform")
    registry.load_external_checks(str(checks_dir.resolve()))  # verified_sources=None

    captured = capsys.readouterr()
    assert "LEGACY_DISK_LOAD" in captured.out
