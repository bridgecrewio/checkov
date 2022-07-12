from __future__ import annotations

from typing import Iterable
from checkov.common.checks.base_check import BaseCheck

from checkov.common.models.enums import CheckCategories
from checkov.circleci_pipelines.registry import registry


class BaseCircleCIPipelinesCheck(BaseCheck):
    def __init__(
        self,
        name: str,
        id: str,
        supported_entities: Iterable[str],
        block_type: str,
        path: str | None = None,
        ) -> None:
        categories = [CheckCategories.SUPPLY_CHAIN]

        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_entities=supported_entities,
            block_type=block_type,
        )
        self.path = path
        registry.register(self)
