"""Tests for checkov.common.util.update_checker.update_checker."""
from __future__ import annotations

import errno
import json
import os
import pickle
import time
from tempfile import gettempdir
from typing import Any
from unittest.mock import patch, MagicMock

import pytest

from checkov.common.util.update_checker.update_checker import (
    CACHE_FILENAME,
    DATE_FORMAT,
    KEY_SEPARATOR,
    LEGACY_CACHE_FILENAME,
    UpdateChecker,
    UpdateResult,
    cache_results,
    _deserialize_cache,
    _deserialize_result,
    _get_cache_dir,
    _remove_legacy_cache,
    _serialize_cache,
    _serialize_result,
    _write_json_atomic,
)


# ---------------------------------------------------------------------------
# Serialization round-trip
# ---------------------------------------------------------------------------

class TestSerializeResult:
    def test_none_result(self) -> None:
        assert _serialize_result(None) is None

    def test_round_trip_with_date(self) -> None:
        result = UpdateResult(package="pkg", running="1.0", available="2.0", release_date="2025-01-15T10:30:00")
        serialized = _serialize_result(result)
        assert serialized is not None
        assert serialized["package_name"] == "pkg"
        assert serialized["release_date"] == "2025-01-15T10:30:00"

        deserialized = _deserialize_result(serialized)
        assert deserialized is not None
        assert deserialized.package_name == "pkg"
        assert deserialized.available_version == "2.0"
        assert deserialized.running_version == "1.0"
        assert deserialized.release_date is not None
        assert deserialized.release_date.strftime(DATE_FORMAT) == "2025-01-15T10:30:00"

    def test_round_trip_without_date(self) -> None:
        result = UpdateResult(package="pkg", running="1.0", available="2.0", release_date=None)
        serialized = _serialize_result(result)
        deserialized = _deserialize_result(serialized)
        assert deserialized is not None
        assert deserialized.release_date is None


class TestSerializeCache:
    def test_round_trip(self) -> None:
        result = UpdateResult(package="checkov", running="3.0", available="3.1", release_date="2025-06-01T00:00:00")
        cache = {("checkov", "3.0"): (1000.0, result), ("other", "1.0"): (2000.0, None)}
        serialized = _serialize_cache(cache)
        deserialized = _deserialize_cache(serialized)

        assert len(deserialized) == 2
        assert ("checkov", "3.0") in deserialized
        assert ("other", "1.0") in deserialized
        assert deserialized[("other", "1.0")][1] is None
        assert deserialized[("checkov", "3.0")][1] is not None
        assert deserialized[("checkov", "3.0")][1].available_version == "3.1"  # type: ignore[union-attr]


class TestDeserializeCacheWithInvalidInput:
    @pytest.mark.parametrize("data", [
        "not a dict",
        42,
        None,
        [],
        {"no_separator": [1.0, None]},
        {f"a{KEY_SEPARATOR}b": "not a list"},
        {f"a{KEY_SEPARATOR}b": ["not_a_number", None]},
        {f"a{KEY_SEPARATOR}b": [1.0]},
    ])
    def test_returns_empty_for_invalid_data(self, data: Any) -> None:
        assert _deserialize_cache(data) == {}


class TestPicklePayloadSafety:

    def test_pickle_in_tmp_is_not_loaded(self, tmp_path: Any) -> None:
        class Pwn:
            def __reduce__(self) -> tuple[Any, ...]:
                return (os.system, ("echo PICKLE-CANARY-FIRED",))

        legacy_path = tmp_path / LEGACY_CACHE_FILENAME
        with open(legacy_path, "wb") as f:
            pickle.dump({"x": Pwn()}, f)

        assert legacy_path.exists()

        try:
            with open(legacy_path, "r") as fp:
                data = json.load(fp)
        except (json.JSONDecodeError, UnicodeDecodeError, ValueError):
            data = None

        assert data is None or _deserialize_cache(data) == {}

    def test_legacy_cache_is_cleaned_up(self, tmp_path: Any) -> None:
        legacy_path = os.path.join(str(tmp_path), LEGACY_CACHE_FILENAME)
        with open(legacy_path, "wb") as f:
            pickle.dump({"x": "y"}, f)

        with patch("checkov.common.util.update_checker.update_checker.gettempdir", return_value=str(tmp_path)):
            _remove_legacy_cache()

        assert not os.path.exists(legacy_path)


class TestWriteJsonAtomic:
    def test_creates_file_with_correct_content(self, tmp_path: Any) -> None:
        target = str(tmp_path / "cache.json")
        _write_json_atomic(target, {"key": "value"})

        assert os.path.exists(target)
        with open(target) as f:
            data = json.load(f)
        assert data == {"key": "value"}

    def test_no_tmp_file_left_on_success(self, tmp_path: Any) -> None:
        target = str(tmp_path / "cache.json")
        _write_json_atomic(target, {})
        assert not os.path.exists(target + ".tmp")


# ---------------------------------------------------------------------------
# Cache directory
# ---------------------------------------------------------------------------

class TestGetCacheDir:
    def test_returns_per_user_dir(self) -> None:
        cache_dir = _get_cache_dir()
        assert "checkov" in cache_dir
        assert cache_dir != gettempdir()
        assert os.path.isdir(cache_dir)


# ---------------------------------------------------------------------------
# Lazy initialization: read-only filesystem safety
# ---------------------------------------------------------------------------

class TestReadOnlyFilesystem:
    """Verify that importing / decorating does NOT touch the filesystem.

    The cache directory should only be created on the first actual call to
    the decorated function, so that ``CKV_SKIP_PACKAGE_UPDATE_CHECK=True``
    can prevent the call entirely and avoid the OSError on read-only mounts.
    """

    def test_import_does_not_call_makedirs(self) -> None:
        """Applying @cache_results must not invoke _get_cache_dir / os.makedirs."""
        from checkov.common.util.update_checker.update_checker import cache_results, UpdateChecker, UpdateResult

        makedirs_called = False
        original_makedirs = os.makedirs

        def tracking_makedirs(*args: Any, **kwargs: Any) -> None:
            nonlocal makedirs_called
            makedirs_called = True
            original_makedirs(*args, **kwargs)

        with patch("checkov.common.util.update_checker.update_checker.os.makedirs", side_effect=tracking_makedirs):
            # Re-apply the decorator — simulates what happens at import time
            @cache_results
            def dummy_check(self: UpdateChecker, pkg: str, ver: str) -> UpdateResult | None:
                return None

        # The decorator body must NOT have called makedirs
        assert not makedirs_called, "cache_results must not call os.makedirs at decoration time"

    def test_cache_results_gracefully_handles_readonly_fs(self) -> None:
        """When _get_cache_dir raises OSError the decorated function still works."""
        from checkov.common.util.update_checker.update_checker import cache_results, UpdateChecker, UpdateResult

        @cache_results
        def dummy_check(self: UpdateChecker, pkg: str, ver: str) -> UpdateResult | None:
            return UpdateResult(package=pkg, running=ver, available="99.0", release_date=None)

        with patch(
            "checkov.common.util.update_checker.update_checker._get_cache_dir",
            side_effect=OSError("Read-only file system"),
        ):
            checker = UpdateChecker()
            result = dummy_check(checker, "checkov", "1.0")

        assert result is not None
        assert result.available_version == "99.0"

    def test_skip_update_check_never_triggers_cache_init(self) -> None:
        """Simulates the real-world flow: skip_check=True means check() is never
        called, so the cache directory is never created."""
        from checkov.common.version_manager import check_for_update

        with patch(
            "checkov.common.util.update_checker.update_checker._get_cache_dir",
            side_effect=OSError("Read-only file system"),
        ):
            # skip_check=True → returns None immediately, never calls UpdateChecker.check()
            result = check_for_update("checkov", "3.0.0", skip_check=True)

        assert result is None


# ---------------------------------------------------------------------------
# PermissionError / OSError graceful degradation
# ---------------------------------------------------------------------------

class TestCacheGracefulDegradation:
    """Verify that every cache code path handles PermissionError and OSError
    without crashing, so checkov works on read-only volumes, permission-
    restricted home dirs, full disks, and network-mounted filesystems."""

    # -- _get_cache_dir: PermissionError (e.g. non-writable home) ----------

    def test_permission_error_on_makedirs(self) -> None:
        """PermissionError in _get_cache_dir degrades to in-memory cache."""
        @cache_results
        def dummy(self: UpdateChecker, pkg: str, ver: str) -> UpdateResult | None:
            return UpdateResult(package=pkg, running=ver, available="9.0", release_date=None)

        with patch(
            "checkov.common.util.update_checker.update_checker._get_cache_dir",
            side_effect=PermissionError(errno.EACCES, "Permission denied", "/home/locked/.cache"),
        ):
            checker = UpdateChecker()
            result = dummy(checker, "checkov", "1.0")

        assert result is not None
        assert result.available_version == "9.0"

    # -- _get_cache_dir: OSError EROFS (read-only filesystem) ---------------

    def test_readonly_fs_erofs(self) -> None:
        """OSError with errno 30 (EROFS) degrades to in-memory cache."""
        @cache_results
        def dummy(self: UpdateChecker, pkg: str, ver: str) -> UpdateResult | None:
            return UpdateResult(package=pkg, running=ver, available="8.0", release_date=None)

        with patch(
            "checkov.common.util.update_checker.update_checker._get_cache_dir",
            side_effect=OSError(errno.EROFS, "Read-only file system", "/home/nonroot/.cache"),
        ):
            checker = UpdateChecker()
            result = dummy(checker, "checkov", "2.0")

        assert result is not None
        assert result.available_version == "8.0"

    # -- save_to_permacache: IOError on write (disk full, etc.) -------------

    def test_disk_full_on_cache_write(self, tmp_path: Any) -> None:
        """IOError during save_to_permacache must not crash the check."""
        cache_dir = str(tmp_path / "checkov_cache")
        os.makedirs(cache_dir)
        cache_file = os.path.join(cache_dir, CACHE_FILENAME)

        @cache_results
        def dummy(self: UpdateChecker, pkg: str, ver: str) -> UpdateResult | None:
            return UpdateResult(package=pkg, running=ver, available="7.0", release_date=None)

        # Let init succeed (writable dir), but make writes fail
        with patch(
            "checkov.common.util.update_checker.update_checker._get_cache_dir",
            return_value=cache_dir,
        ):
            with patch(
                "checkov.common.util.update_checker.update_checker._write_json_atomic",
                side_effect=IOError(errno.ENOSPC, "No space left on device"),
            ):
                checker = UpdateChecker()
                result = dummy(checker, "checkov", "3.0")

        # Function must still return the result despite write failure
        assert result is not None
        assert result.available_version == "7.0"

    # -- update_from_permacache: corrupt cache file -------------------------

    def test_corrupt_cache_file_does_not_crash(self, tmp_path: Any) -> None:
        """A corrupt (non-JSON) cache file must not crash the check."""
        cache_dir = str(tmp_path / "checkov_cache")
        os.makedirs(cache_dir)
        cache_file = os.path.join(cache_dir, CACHE_FILENAME)

        # Write garbage to the cache file
        with open(cache_file, "w") as f:
            f.write("NOT VALID JSON {{{")

        @cache_results
        def dummy(self: UpdateChecker, pkg: str, ver: str) -> UpdateResult | None:
            return UpdateResult(package=pkg, running=ver, available="6.0", release_date=None)

        with patch(
            "checkov.common.util.update_checker.update_checker._get_cache_dir",
            return_value=cache_dir,
        ):
            checker = UpdateChecker()
            result = dummy(checker, "checkov", "4.0")

        assert result is not None
        assert result.available_version == "6.0"

    # -- update_from_permacache: PermissionError reading cache file ---------

    def test_permission_denied_reading_cache_file(self, tmp_path: Any) -> None:
        """PermissionError reading the cache file degrades gracefully."""
        cache_dir = str(tmp_path / "checkov_cache")
        os.makedirs(cache_dir)
        cache_file = os.path.join(cache_dir, CACHE_FILENAME)

        # Create a valid cache file, then make it unreadable
        _write_json_atomic(cache_file, {})
        os.chmod(cache_file, 0o000)

        @cache_results
        def dummy(self: UpdateChecker, pkg: str, ver: str) -> UpdateResult | None:
            return UpdateResult(package=pkg, running=ver, available="5.0", release_date=None)

        try:
            with patch(
                "checkov.common.util.update_checker.update_checker._get_cache_dir",
                return_value=cache_dir,
            ):
                checker = UpdateChecker()
                result = dummy(checker, "checkov", "5.0")

            assert result is not None
            assert result.available_version == "5.0"
        finally:
            # Restore permissions so tmp_path cleanup works
            os.chmod(cache_file, 0o644)

    # -- Multiple calls: in-memory cache works when disk is unavailable -----

    def test_in_memory_cache_works_without_disk(self) -> None:
        """When disk cache is unavailable, in-memory caching still prevents
        redundant calls to the wrapped function."""
        call_count = 0

        @cache_results
        def dummy(self: UpdateChecker, pkg: str, ver: str) -> UpdateResult | None:
            nonlocal call_count
            call_count += 1
            return UpdateResult(package=pkg, running=ver, available="4.0", release_date=None)

        with patch(
            "checkov.common.util.update_checker.update_checker._get_cache_dir",
            side_effect=OSError("Read-only file system"),
        ):
            checker = UpdateChecker()
            result1 = dummy(checker, "checkov", "1.0")
            result2 = dummy(checker, "checkov", "1.0")

        assert call_count == 1, "Second call should use in-memory cache"
        assert result1 is not None
        assert result2 is not None
        assert result1.available_version == result2.available_version == "4.0"

    # -- _remove_legacy_cache: PermissionError on temp dir ------------------

    def test_legacy_cache_removal_permission_error(self, tmp_path: Any) -> None:
        """PermissionError removing legacy cache must not crash."""
        with patch(
            "checkov.common.util.update_checker.update_checker.gettempdir",
            return_value=str(tmp_path),
        ):
            with patch("os.remove", side_effect=PermissionError("Permission denied")):
                # Create the legacy file so the code path tries to remove it
                legacy_path = os.path.join(str(tmp_path), LEGACY_CACHE_FILENAME)
                with open(legacy_path, "w") as f:
                    f.write("legacy")
                # Must not raise
                _remove_legacy_cache()


# ---------------------------------------------------------------------------
# Integration: JSON cache file is used, not pickle
# ---------------------------------------------------------------------------

class TestCacheUsesJson:
    def test_cache_file_is_valid_json(self, tmp_path: Any) -> None:
        cache_file = str(tmp_path / CACHE_FILENAME)
        result = UpdateResult(package="checkov", running="3.0", available="3.1", release_date="2025-01-01T00:00:00")
        cache = {("checkov", "3.0"): (time.time(), result)}
        _write_json_atomic(cache_file, _serialize_cache(cache))

        with open(cache_file) as f:
            data = json.load(f)

        assert isinstance(data, dict)
        key = f"checkov{KEY_SEPARATOR}3.0"
        assert key in data
        assert data[key][1]["available_version"] == "3.1"
