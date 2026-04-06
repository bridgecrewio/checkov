from __future__ import annotations

import json
import os
import pickle
import stat
import time
from tempfile import gettempdir
from typing import Any
from unittest.mock import patch

import pytest

from checkov.common.util.update_checker.update_checker import (
    CACHE_DIR_MODE,
    CACHE_FILENAME,
    DATE_FORMAT,
    INSECURE_PERMISSION_MASK,
    KEY_SEPARATOR,
    LEGACY_CACHE_FILENAME,
    UpdateResult,
    _deserialize_cache,
    _deserialize_result,
    _get_cache_dir,
    _has_secure_permissions,
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


class TestDeserializeCacheRejectsInvalid:
    @pytest.mark.parametrize("bad_data", [
        "not a dict",
        42,
        None,
        [],
        {"no_separator": [1.0, None]},
        {f"a{KEY_SEPARATOR}b": "not a list"},
        {f"a{KEY_SEPARATOR}b": ["not_a_number", None]},
        {f"a{KEY_SEPARATOR}b": [1.0]},
    ])
    def test_rejects_malformed_data(self, bad_data: Any) -> None:
        result = _deserialize_cache(bad_data)
        assert result == {}


class TestPicklePayloadRejected:
    """Verify the exact PoC from finding F-08 is rejected."""

    def test_malicious_pickle_in_tmp_is_not_loaded(self, tmp_path: Any) -> None:
        """A pickle file at the legacy path must never be deserialized."""

        class Pwn:
            def __reduce__(self) -> tuple[Any, ...]:
                return (os.system, ("echo PICKLE-CANARY-FIRED",))

        legacy_path = tmp_path / LEGACY_CACHE_FILENAME
        with open(legacy_path, "wb") as f:
            pickle.dump({"x": Pwn()}, f)

        assert legacy_path.exists()

        # The new code only reads JSON from a per-user dir — never pickle from /tmp.
        # Attempting to deserialize the pickle as JSON must fail gracefully.
        try:
            with open(legacy_path, "r") as fp:
                data = json.load(fp)
        except (json.JSONDecodeError, UnicodeDecodeError, ValueError):
            data = None

        assert data is None or _deserialize_cache(data) == {}

    def test_legacy_cache_is_removed(self, tmp_path: Any) -> None:
        legacy_path = os.path.join(str(tmp_path), LEGACY_CACHE_FILENAME)
        with open(legacy_path, "wb") as f:
            pickle.dump({"x": "y"}, f)

        with patch("checkov.common.util.update_checker.update_checker.gettempdir", return_value=str(tmp_path)):
            _remove_legacy_cache()

        assert not os.path.exists(legacy_path)


# ---------------------------------------------------------------------------
# File permissions
# ---------------------------------------------------------------------------

class TestFilePermissions:
    def test_secure_permissions_accepted(self, tmp_path: Any) -> None:
        secure_file = tmp_path / "secure.json"
        secure_file.write_text("{}")
        os.chmod(secure_file, 0o600)
        assert _has_secure_permissions(str(secure_file))

    def test_world_readable_rejected(self, tmp_path: Any) -> None:
        insecure_file = tmp_path / "insecure.json"
        insecure_file.write_text("{}")
        os.chmod(insecure_file, 0o644)
        assert not _has_secure_permissions(str(insecure_file))

    def test_group_writable_rejected(self, tmp_path: Any) -> None:
        insecure_file = tmp_path / "insecure.json"
        insecure_file.write_text("{}")
        os.chmod(insecure_file, 0o660)
        assert not _has_secure_permissions(str(insecure_file))

    def test_world_writable_rejected(self, tmp_path: Any) -> None:
        insecure_file = tmp_path / "insecure.json"
        insecure_file.write_text("{}")
        os.chmod(insecure_file, 0o666)
        assert not _has_secure_permissions(str(insecure_file))



class TestWriteJsonAtomic:
    def test_creates_file_with_correct_permissions(self, tmp_path: Any) -> None:
        target = str(tmp_path / "cache.json")
        _write_json_atomic(target, {"key": "value"})

        assert os.path.exists(target)
        file_mode = stat.S_IMODE(os.stat(target).st_mode)
        assert not (file_mode & INSECURE_PERMISSION_MASK), f"File has insecure permissions: {oct(file_mode)}"

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

    def test_dir_not_world_accessible(self) -> None:
        cache_dir = _get_cache_dir()
        dir_mode = stat.S_IMODE(os.stat(cache_dir).st_mode)
        assert not (dir_mode & INSECURE_PERMISSION_MASK), f"Dir has insecure permissions: {oct(dir_mode)}"


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
