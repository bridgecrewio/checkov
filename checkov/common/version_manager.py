from __future__ import annotations

from checkov.common.util.update_checker import UpdateChecker
from checkov.common.util.env_vars_config import env_vars_config


def check_for_update(package: str, version: str) -> str | None:
    if env_vars_config.SKIP_PACKAGE_UPDATE_CHECK:
        return None

    try:
        checker = UpdateChecker()
        result = checker.check(package, version)
        if result is None:
            return None

        return result.available_version
    except Exception:  # nosec
        return None
