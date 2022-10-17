from __future__ import annotations

from abc import abstractmethod
from collections.abc import Iterable
from typing import TYPE_CHECKING, Any

from checkov.common.checks.base_check import BaseCheck
from checkov.azure_pipelines.checks.registry import registry

if TYPE_CHECKING:
    from checkov.common.models.enums import CheckCategories, CheckResult


class BaseAzurePipelinesCheck(BaseCheck):
    def __init__(
        self,
        name: str,
        id: str,
        categories: Iterable[CheckCategories],
        supported_entities: Iterable[str],
        block_type: str,
        path: str | None = None,
    ) -> None:
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_entities=supported_entities,
            block_type=block_type,
        )
        self.path = path
        registry.register(self)

    def scan_entity_conf(self, conf: dict[str, Any], entity_type: str) -> tuple[CheckResult, dict[str, Any]]:  # type:ignore[override]  # multi_signature decorator is problematic
        self.entity_type = entity_type

        return self.scan_conf(conf)

    @abstractmethod
    def scan_conf(self, conf: dict[str, Any]) -> tuple[CheckResult, dict[str, Any]]:
        pass
