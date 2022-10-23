from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING

from checkov.common.checks.base_check import BaseCheck
from checkov.dockerfile.registry import registry

if TYPE_CHECKING:
    from checkov.common.models.enums import CheckCategories


class BaseDockerfileCheck(BaseCheck):
    def __init__(
        self,
        name: str,
        id: str,
        categories: Iterable[CheckCategories],
        supported_instructions: Iterable[str],
        guideline: str | None = None,
    ) -> None:
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_entities=supported_instructions,
            block_type="dockerfile",
            guideline=guideline,
        )
        self.supported_instructions = supported_instructions
        registry.register(self)
