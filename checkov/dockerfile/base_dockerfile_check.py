from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING

from checkov.common.checks.base_check import BaseCheck
from checkov.common.models.enums import CheckResult
from checkov.dockerfile.registry import registry

if TYPE_CHECKING:
    from checkov.common.models.enums import CheckCategories
    from dockerfile_parse.parser import _Instruction


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

    def scan_entity_conf(  # type:ignore[override]  # it's ok
        self, conf: list[_Instruction], entity_type: str
    ) -> tuple[CheckResult, list[_Instruction] | None]:
        self.entity_type = entity_type

        return self.scan_resource_conf(conf)

    def scan_resource_conf(self, conf: list[_Instruction]) -> tuple[CheckResult, list[_Instruction] | None]:
        # this is not an abstractmethod to be backward compatible
        return CheckResult.PASSED, None
