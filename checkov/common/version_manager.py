from __future__ import annotations

from checkov.common.util.update_checker import UpdateChecker


def check_for_update(package: str, version: str, skip_check: bool) -> str | None:
    if skip_check:
        return None

    try:
        checker = UpdateChecker()
        result = checker.check(package, version)
        if result is None:
            return None

        return result.available_version
    except Exception:  # nosec
        return None
