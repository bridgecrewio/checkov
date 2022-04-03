#
# No change required normally except CheckCategories.XXXXX line 13
#
from __future__ import annotations

from collections.abc import Iterable

from checkov.common.checks.base_check import BaseCheck
from checkov.common.models.enums import CheckCategories

# Change the class name to your runner
# Eg. BaseXXXXXXXXXXXXXCheck
class BaseExampleRunnerCheck(BaseCheck):
    def __init__(
        self, name: str, id: str, supported_entities: Iterable[str], block_type: str, path: str | None = None
    ) -> None:
        # Set category for new checks
        # Look at checkov/common/models/enums.py for options
        categories = (CheckCategories.SUPPLY_CHAIN,)

        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_entities=supported_entities,
            block_type=block_type,
        )
        self.path = path
