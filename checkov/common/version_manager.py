from __future__ import annotations

from update_checker import UpdateChecker


def check_for_update(package: str, version: str) -> str | None:
    try:
        checker = UpdateChecker()
        result = checker.check(package, version)
        return result.available_version
    except Exception:  # nosec
        return None
