from __future__ import annotations

from typing import Iterable

from checkov.common.checks.base_check import BaseCheck
from checkov.common.models.enums import CheckCategories

from checkov.github.registry import registry


class BaseGithubCheck(BaseCheck):
    def __init__(self, name: str, id: str, categories: Iterable[CheckCategories], supported_entities: Iterable[str],
                 block_type: str, path: str | None = None, guideline: str | None = None) -> None:
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_entities=supported_entities,
            block_type=block_type,
            guideline=guideline,
        )
        self.path = path
        registry.register(self)
