"""Module that checks if there is an updated version of a package available."""
from __future__ import annotations

import json
import os
import re
import sys
import time
from collections.abc import Generator, Callable
from datetime import datetime
from functools import wraps
from tempfile import gettempdir
from typing import Any

import platformdirs
import requests

CACHE_DIR_NAME = "checkov"
CACHE_FILENAME = "update_checker_cache.json"
LEGACY_CACHE_FILENAME = "update_checker_cache.pkl"
CACHE_EXPIRE_SECONDS = 3600
KEY_SEPARATOR = "||"
DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"


def _get_cache_dir() -> str:
    """Return a per-user cache directory, creating it if needed."""
    cache_dir = platformdirs.user_cache_dir(CACHE_DIR_NAME)
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir


def _remove_legacy_cache() -> None:
    try:
        legacy_path = os.path.join(gettempdir(), LEGACY_CACHE_FILENAME)
        if os.path.exists(legacy_path):
            os.remove(legacy_path)
    except OSError:
        pass


def _serialize_result(result: UpdateResult | None) -> dict[str, Any] | None:
    if result is None:
        return None
    return {
        "package_name": result.package_name,
        "running_version": result.running_version,
        "available_version": result.available_version,
        "release_date": result.release_date.strftime(DATE_FORMAT) if result.release_date else None,
    }


def _deserialize_result(data: Any) -> UpdateResult | None:
    if not isinstance(data, dict):
        return None
    required = {"package_name", "running_version", "available_version", "release_date"}
    if not required.issubset(data.keys()):
        return None
    return UpdateResult(
        package=str(data["package_name"]),
        running=str(data["running_version"]),
        available=str(data["available_version"]),
        release_date=data.get("release_date"),
    )


def _serialize_cache(cache: dict[tuple[str, str], tuple[float, UpdateResult | None]]) -> dict[str, Any]:
    return {
        f"{pkg}{KEY_SEPARATOR}{ver}": [ts, _serialize_result(result)]
        for (pkg, ver), (ts, result) in cache.items()
    }


def _deserialize_cache(data: Any) -> dict[tuple[str, str], tuple[float, UpdateResult | None]]:
    cache: dict[tuple[str, str], tuple[float, UpdateResult | None]] = {}
    if not isinstance(data, dict):
        return cache
    for key, value in data.items():
        if not isinstance(key, str) or KEY_SEPARATOR not in key:
            continue
        parts = key.split(KEY_SEPARATOR, 1)
        if not isinstance(value, list) or len(value) != 2 or not isinstance(value[0], (int, float)):
            continue
        cache[(parts[0], parts[1])] = (float(value[0]), _deserialize_result(value[1]))
    return cache


def _write_json_atomic(path: str, data: Any) -> None:
    """Write JSON to *path* atomically via a temp file to avoid corruption."""
    tmp_path = path + ".tmp"
    with open(tmp_path, "w") as fp:
        json.dump(data, fp)
    os.replace(tmp_path, path)


def cache_results(
    function: Callable[[UpdateChecker, str, str], UpdateResult | None]
) -> Callable[[UpdateChecker, str, str], UpdateResult | None]:
    """Return decorated function that caches the results."""

    def _ensure_initialized() -> None:
        """Lazily initialize the cache directory and load the permacache on first use.

        """
        if _state["initialized"]:
            return
        _state["initialized"] = True
        try:
            _remove_legacy_cache()
            _state["filename"] = os.path.join(_get_cache_dir(), CACHE_FILENAME)
            update_from_permacache()
        except (NotImplementedError, OSError):
            _state["filename"] = None

    def save_to_permacache() -> None:
        """Merge in-memory cache into the on-disk permacache."""
        update_from_permacache()
        try:
            if _state["filename"] is None:
                return
            _write_json_atomic(_state["filename"], _serialize_cache(cache))
        except IOError:
            pass

    def update_from_permacache() -> None:
        """Load newer entries from the on-disk permacache into memory."""
        try:
            if _state["filename"] is None:
                return
            with open(_state["filename"], "r") as fp:
                permacache = _deserialize_cache(json.load(fp))
        except Exception:
            return
        for key, value in permacache.items():
            if key not in cache or value[0] > cache[key][0]:
                cache[key] = value

    cache: dict[tuple[str, str], tuple[float, UpdateResult | None]] = {}
    _state: dict[str, Any] = {"initialized": False, "filename": None}

    @wraps(function)
    def wrapped(obj: UpdateChecker, package_name: str, package_version: str, **extra_data: Any) -> UpdateResult | None:
        """Return cached results if available."""
        _ensure_initialized()
        now = time.time()
        key = (package_name, package_version)
        if not obj._bypass_cache and key in cache:
            cache_time, retval = cache[key]
            if now - cache_time < CACHE_EXPIRE_SECONDS:
                return retval
        retval = function(obj, package_name, package_version, **extra_data)
        cache[key] = now, retval
        if _state["filename"]:
            save_to_permacache()
        return retval

    return wrapped


def query_pypi(package: str, include_prereleases: bool) -> dict[str, Any]:
    """Return information about the current version of package."""
    try:
        response = requests.get(f"https://pypi.org/pypi/{package}/json", timeout=1)
    except requests.exceptions.RequestException:
        return {"success": False}
    if response.status_code != 200:
        return {"success": False}
    data = response.json()
    versions = list(data["releases"].keys())
    versions.sort(key=parse_version, reverse=True)

    version = versions[0]
    for tmp_version in versions:
        if include_prereleases or standard_release(tmp_version):
            version = tmp_version
            break

    upload_time = None
    for file_info in data["releases"][version]:
        if file_info["upload_time"]:
            upload_time = file_info["upload_time"]
            break

    return {"success": True, "data": {"upload_time": upload_time, "version": version}}


def standard_release(version: str) -> bool:
    return version.replace(".", "").isdigit()


class UpdateResult:
    """Contains the information for a package that has an update."""

    def __init__(self, package: str, running: str, available: str, release_date: str | None) -> None:
        self.available_version = available
        self.package_name = package
        self.running_version = running
        self.release_date: datetime | None = (
            datetime.strptime(release_date, DATE_FORMAT) if release_date else None
        )

    def __str__(self) -> str:
        """Return a printable UpdateResult string."""
        retval = f"Version {self.running_version} of {self.package_name} is outdated. Version {self.available_version} "
        if self.release_date:
            retval += f"was released {pretty_date(self.release_date)}."
        else:
            retval += "is available."
        return retval


class UpdateChecker:
    """A class to check for package updates."""

    def __init__(self, *, bypass_cache: bool = False) -> None:
        self._bypass_cache = bypass_cache

    @cache_results
    def check(self, package_name: str, package_version: str) -> UpdateResult | None:
        """Return a UpdateResult object if there is a newer version."""

        data = query_pypi(package_name, include_prereleases=not standard_release(package_version))

        if not data.get("success") or (parse_version(package_version) >= parse_version(data["data"]["version"])):
            return None

        return UpdateResult(
            package_name,
            running=package_version,
            available=data["data"]["version"],
            release_date=data["data"]["upload_time"],
        )


def pretty_date(the_datetime: datetime) -> str:
    """Attempt to return a human-readable time delta string."""
    # Source modified from
    # http://stackoverflow.com/a/5164027/176978
    diff = datetime.utcnow() - the_datetime
    if diff.days > 7 or diff.days < 0:
        return the_datetime.strftime("%A %B %d, %Y")
    elif diff.days == 1:
        return "1 day ago"
    elif diff.days > 1:
        return f"{diff.days} days ago"
    elif diff.seconds <= 1:
        return "just now"
    elif diff.seconds < 60:
        return f"{diff.seconds} seconds ago"
    elif diff.seconds < 120:
        return "1 minute ago"
    elif diff.seconds < 3600:
        return f"{int(round(diff.seconds / 60))} minutes ago"
    elif diff.seconds < 7200:
        return "1 hour ago"
    else:
        return f"{int(round(diff.seconds / 3600))} hours ago"


def update_check(package_name: str, package_version: str, bypass_cache: bool = False) -> None:
    """Convenience method that outputs to stderr if an update is available."""
    checker = UpdateChecker(bypass_cache=bypass_cache)
    result = checker.check(package_name, package_version)
    if result:
        print(result, file=sys.stderr)


# The following section of code is taken from setuptools pkg_resources.py (PSF
# license). Unfortunately importing pkg_resources to directly use the
# parse_version function results in some undesired side effects.

component_re = re.compile(r"(\d+ | [a-z]+ | \.| -)", re.VERBOSE)
replace = {"pre": "c", "preview": "c", "-": "final-", "rc": "c", "dev": "@"}.get


def _parse_version_parts(s: str) -> Generator[str, None, None]:
    for part in component_re.split(s):
        part = replace(part, part)
        if not part or part == ".":
            continue
        if part[:1] in "0123456789":
            yield part.zfill(8)  # pad for numeric comparison
        else:
            yield "*" + part

    yield "*final"  # ensure that alpha/beta/candidate are before final


def parse_version(s: str) -> tuple[str, ...]:
    """Convert a version string to a chronologically-sortable key.

    This is a rough cross between distutils' StrictVersion and LooseVersion;
    if you give it versions that would work with StrictVersion, then it behaves
    the same; otherwise it acts like a slightly-smarter LooseVersion. It is
    *possible* to create pathological version coding schemes that will fool
    this parser, but they should be very rare in practice.

    The returned value will be a tuple of strings.  Numeric portions of the
    version are padded to 8 digits so they will compare numerically, but
    without relying on how numbers compare relative to strings.  Dots are
    dropped, but dashes are retained.  Trailing zeros between alpha segments
    or dashes are suppressed, so that e.g. "2.4.0" is considered the same as
    "2.4". Alphanumeric parts are lower-cased.

    The algorithm assumes that strings like "-" and any alpha string that
    alphabetically follows "final"  represents a "patch level".  So, "2.4-1"
    is assumed to be a branch or patch of "2.4", and therefore "2.4.1" is
    considered newer than "2.4-1", which in turn is newer than "2.4".

    Strings like "a", "b", "c", "alpha", "beta", "candidate" and so on (that
    come before "final" alphabetically) are assumed to be pre-release versions,
    so that the version "2.4" is considered newer than "2.4a1".

    Finally, to handle miscellaneous cases, the strings "pre", "preview", and
    "rc" are treated as if they were "c", i.e. as though they were release
    candidates, and therefore are not as new as a version string that does not
    contain them, and "dev" is replaced with an '@' so that it sorts lower than
    than any other pre-release tag.

    """
    parts: list[str] = []
    for part in _parse_version_parts(s.lower()):
        if part.startswith("*"):
            if part < "*final":  # remove '-' before a prerelease tag
                while parts and parts[-1] == "*final-":
                    parts.pop()
            # remove trailing zeros from each series of numeric parts
            while parts and parts[-1] == "00000000":
                parts.pop()
        parts.append(part)
    return tuple(parts)
