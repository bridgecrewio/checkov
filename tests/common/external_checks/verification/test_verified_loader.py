"""Tests for the in-memory verified-sources loader and meta-path finder.

Covers Phase 2 of the verification module:

* Direct load via ``load_verified_sources_into_module`` execs the
  in-memory bytes, not the on-disk file (verify-then-load consistency
  for direct loads).
* ``VerifiedSourcesFinder``, while installed, serves an ``import``
  request from the in-memory map (verify-then-load consistency for
  transitive imports like ``import _helper`` from inside a verified
  check).
* ``BaseCheckRegistry.load_external_checks`` with ``verified_sources``
  refuses any on-disk ``.py`` file that is absent from the allowlist.
* The finder is fully cleaned up from ``sys.meta_path`` after
  ``load_external_checks`` returns — no leakage into the rest of the
  Python program.
* The unverified default disk-load path (``verified_sources=None``) is
  byte-for-byte unchanged. This is the supported path when no public
  key is configured — see ``base_check_registry._load_external_checks_from_disk``.
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
    on_disk = tmp_path / "module_a.py"
    on_disk.write_bytes(b"VALUE = 'disk'\n")
    in_memory_bytes = b"VALUE = 'memory'\nFLAG = 42\n"

    module = load_verified_sources_into_module(
        "module_a_test_in_memory", str(on_disk), in_memory_bytes,
    )

    assert module.VALUE == "memory"  # in-memory bytes won
    assert module.FLAG == 42
    assert module.__file__ == str(on_disk)


def test_load_verified_sources_into_module_writes_no_bytecode_cache(tmp_path: Path):
    """The loader must NOT write a ``.pyc`` next to the source.

    A persistent bytecode cache on disk is a second representation of the
    module that does not carry a trailer of its own. Disabling cache writes
    keeps the executed-bytes / verified-bytes equality strictly per-process
    and avoids leaving artefacts in customer directories.
    """
    on_disk = tmp_path / "no_cache_target.py"
    on_disk.write_bytes(b"VALUE = 'verified'\n")

    load_verified_sources_into_module(
        "no_cache_target_mod", str(on_disk), b"VALUE = 'verified'\n",
    )

    # No __pycache__ directory created next to the source.
    assert not (tmp_path / "__pycache__").exists(), (
        f"unexpected __pycache__ in {tmp_path}: "
        f"{list((tmp_path / '__pycache__').iterdir()) if (tmp_path / '__pycache__').exists() else []}"
    )
    # And no stray .pyc anywhere in tmp_path.
    pyc_files = list(tmp_path.rglob("*.pyc"))
    assert pyc_files == [], f"unexpected .pyc files written: {pyc_files}"


def test_load_verified_sources_into_module_cleans_up_on_failure(tmp_path: Path):
    """A SyntaxError in the bytes leaves no half-loaded module behind."""
    on_disk = tmp_path / "broken.py"
    on_disk.write_bytes(b"# empty\n")

    with pytest.raises(SyntaxError):
        load_verified_sources_into_module(
            "module_a_test_broken",
            str(on_disk),
            b"def broken(:\n",  # SyntaxError
        )

    assert "module_a_test_broken" not in sys.modules


def test_verified_source_loader_exec_module_cleans_up_on_failure(tmp_path: Path):
    """``_VerifiedSourceLoader.exec_module`` must mirror the direct loader's
    half-load cleanup — a SyntaxError or in-module raise during the finder
    path must NOT leave a partially initialised module in ``sys.modules``.

    Pins S6: without the cleanup, a single broken verified file could
    poison subsequent legitimate imports of the same name with a
    half-initialised module object.
    """
    import importlib.util
    from checkov.common.external_checks.verification.verified_loader import (
        _VerifiedSourceLoader,
    )

    module_name = "broken_via_finder_exec"
    loader = _VerifiedSourceLoader(
        module_name, str(tmp_path / "broken.py"), b"def broken(:\n",
    )
    spec = importlib.util.spec_from_loader(module_name, loader)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        with pytest.raises(SyntaxError):
            loader.exec_module(module)
        assert module_name not in sys.modules, (
            f"{module_name} survived a SyntaxError during exec_module; "
            f"future imports of this name would receive the half-initialised "
            f"module object instead of a clean ModuleNotFoundError"
        )
    finally:
        sys.modules.pop(module_name, None)


def test_finder_resolves_imports_from_in_memory_map(tmp_path: Path):
    """A normal ``import`` call goes through the finder when active."""
    on_disk = tmp_path / "helper_module.py"
    on_disk.write_bytes(b"raise RuntimeError('disk path was executed')\n")
    in_memory_bytes = b"VALUE = 'from-map'\n"

    finder = install_finder(
        {str(on_disk): in_memory_bytes},
        [str(tmp_path)],
    )
    try:
        module_name = "helper_module_test_in_memory"
        # The finder maps the import name 'helper_module' (via filename
        # 'helper_module.py') to the in-memory bytes; we use a uniquified
        # alias to avoid colliding with another test's sys.modules entry.
        import importlib
        spec = finder.find_spec("helper_module")
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
    """install_finder + uninstall_finder leaves sys.meta_path as it was.

    Uses identity-based comparison (``id()``) rather than ``==`` /
    ``in``. List equality and the ``in`` operator both invoke ``__eq__``
    on every element of ``sys.meta_path``; on Python 3.9 inside xdist
    workers we have observed third-party MetaPathFinder instances whose
    ``__eq__`` can hang indefinitely (waiting on a lock held by an
    xdist control thread). Identity comparison avoids the user-defined
    equality path entirely while still verifying the contract: the
    finder we installed is gone, and the rest of the meta-path is the
    same set of objects in the same order.
    """
    before_ids = [id(x) for x in sys.meta_path]
    finder = install_finder({}, [str(tmp_path)])
    assert id(finder) in [id(x) for x in sys.meta_path]
    uninstall_finder(finder)
    after_ids = [id(x) for x in sys.meta_path]
    assert id(finder) not in after_ids
    assert after_ids == before_ids


def test_uninstall_finder_is_idempotent(tmp_path: Path):
    """Calling uninstall twice does not raise."""
    finder = install_finder({}, [str(tmp_path)])
    uninstall_finder(finder)
    uninstall_finder(finder)  # second call must be a no-op


def test_resolve_verified_source_only_honours_canonical_keys(tmp_path: Path, stub_registry):
    """``_resolve_verified_source`` returns None for non-canonical keys.

    Pins S1: the lookup is documented as "registry keys are realpath",
    full stop. A raw-path fallback (``verified_sources.get(canonical)
    or verified_sources.get(raw)``) would silently honour any dict key
    that exactly matched the requested ``check_full_path``, even when
    that key was never realpath-normalised by the registry. Such keys
    cannot exist in the production registry (per
    ``sources_registry.verify_and_register``), so a fallback is dead
    code at best — and a footgun if a future caller mutates the
    in-memory map with non-canonical keys.

    To distinguish a raw key from its canonical form we point a symlink
    at a real file and key the dict by the symlinked path. The lookup
    canonicalises via ``realpath`` (resolves the symlink) and so the
    raw symlinked key MUST NOT match.
    """
    import os

    real = tmp_path / "real_check.py"
    real.write_bytes(b"# real signed body\n")
    link = tmp_path / "alias_check.py"
    try:
        os.symlink(real, link)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks not supported on this platform")

    registry = stub_registry

    # Key the dict by the SYMLINKED (raw) path — the registry would
    # never have produced this key because verify_and_register
    # realpath-normalises every key.
    raw_link_path = str(link)
    verified_sources = {raw_link_path: b"unverified-bytes-the-registry-never-issued"}

    result = registry._resolve_verified_source(verified_sources, raw_link_path)

    assert result is None, (
        "non-canonical (symlinked) key lookup must return None — the "
        "raw-path fallback is removed; if this fails the fallback has "
        "been reintroduced and S1 has regressed"
    )

    # Sanity: when the dict IS keyed by the realpath, the lookup finds it.
    canonical_path = os.path.normpath(os.path.realpath(raw_link_path))
    canonical_sources = {canonical_path: b"verified-canonical-bytes"}
    assert (
        registry._resolve_verified_source(canonical_sources, raw_link_path)
        == b"verified-canonical-bytes"
    )


def test_load_external_checks_with_verified_sources_runs_in_memory(
    tmp_path: Path, capsys, stub_registry,
):
    """The registry loader execs the allowlist bytes, ignoring disk content."""
    checks_dir = tmp_path / "checks"
    checks_dir.mkdir()
    (checks_dir / "__init__.py").write_bytes(b"")
    on_disk_check = checks_dir / "verified_check.py"
    on_disk_check.write_bytes(b"print('FROM_DISK')\n")  # would be visible if exec'd
    in_memory_bytes = b"print('FROM_MEMORY')\n"

    verified_sources = {
        str(on_disk_check.resolve()): in_memory_bytes,
    }

    stub_registry.load_external_checks(
        str(checks_dir.resolve()), verified_sources=verified_sources,
    )

    captured = capsys.readouterr()
    assert "FROM_MEMORY" in captured.out
    assert "FROM_DISK" not in captured.out


def test_load_external_checks_refuses_unverified_file(
    tmp_path: Path, caplog, stub_registry,
):
    """A .py file present on disk but absent from verified_sources is REFUSED and ESCALATES.

    Two-part contract:
    1. The bytes are NEVER exec'd — refused at the resolve step.
    2. The loader raises ``SignatureVerificationError`` at the end of the
       walk so the chokepoint can route the failure through
       ``_report_verification_failure_and_exit`` and exit 2.

    Part 2 closes the M1/S3 disk-drift gap: an empty allowlist or a
    late-added on-disk file (rename / git stash pop / build-script
    artefact / unrelated process write) must not silently shrink the
    verified check set.
    """
    import logging
    from checkov.common.external_checks.verification import (
        SignatureVerificationError,
    )

    checks_dir = tmp_path / "checks"
    checks_dir.mkdir()
    (checks_dir / "__init__.py").write_bytes(b"")
    extra = checks_dir / "unverified_extra.py"
    # Bytes that would *raise* if executed — proves the loader did not exec.
    extra.write_bytes(b"raise RuntimeError('unverified file was executed')\n")

    with caplog.at_level(logging.ERROR), pytest.raises(SignatureVerificationError) as exc:
        stub_registry.load_external_checks(
            str(checks_dir.resolve()),
            verified_sources={},  # empty allowlist → every .py is unverified
        )

    # The escalation diagnostic must name the offending file so the
    # operator sees exactly what diverged on disk.
    assert "unverified_extra.py" in str(exc.value)
    # And the per-file ERROR log line remains as a UX nicety.
    assert any(
        "Refusing to load unverified external check" in record.message
        for record in caplog.records
    )


def test_load_external_checks_cleans_up_finder(tmp_path: Path, stub_registry):
    """sys.meta_path returns to its pre-call state once load returns."""
    checks_dir = tmp_path / "checks"
    checks_dir.mkdir()
    (checks_dir / "__init__.py").write_bytes(b"")
    chk = checks_dir / "simple.py"
    chk.write_bytes(b"X = 1\n")

    before = list(sys.meta_path)
    stub_registry.load_external_checks(
        str(checks_dir.resolve()),
        verified_sources={str(chk.resolve()): b"X = 1\n"},
    )
    after = list(sys.meta_path)

    # No VerifiedSourcesFinder may remain on sys.meta_path.
    assert not any(isinstance(f, VerifiedSourcesFinder) for f in after)
    # And the path stack must be unchanged in identity-of-finders too.
    assert len(after) == len(before)


def test_unverified_load_external_checks_unchanged_when_no_verified_sources(
    tmp_path: Path, capsys, stub_registry,
):
    """Default behaviour (no verified_sources) execs from disk as before.

    This is the supported path for operators who don't pass
    ``--external-checks-public-key``; it must remain byte-identical to
    pre-feature behaviour so existing customers see no change.
    """
    checks_dir = tmp_path / "checks"
    checks_dir.mkdir()
    (checks_dir / "__init__.py").write_bytes(b"")
    chk = checks_dir / "unverified_check.py"
    chk.write_bytes(b"print('UNVERIFIED_DISK_LOAD')\n")

    stub_registry.load_external_checks(str(checks_dir.resolve()))  # verified_sources=None

    captured = capsys.readouterr()
    assert "UNVERIFIED_DISK_LOAD" in captured.out
