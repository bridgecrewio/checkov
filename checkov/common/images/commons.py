from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING

from checkov.common.bridgecrew.check_type import CheckType

if TYPE_CHECKING:
    from checkov.common.bridgecrew.platform_integration import BcPlatformIntegration


def enable_image_referencer(
    bc_integration: BcPlatformIntegration, frameworks: Iterable[str] | None, skip_frameworks: Iterable[str] | None
) -> bool:
    """Checks, if Image Referencer should be enabled"""

    if skip_frameworks and CheckType.SCA_IMAGE in skip_frameworks:
        return False

    if bc_integration.bc_api_key:
        if not frameworks:
            return True
        if any(framework in frameworks for framework in ("all", CheckType.SCA_IMAGE)):
            return True

    return False
