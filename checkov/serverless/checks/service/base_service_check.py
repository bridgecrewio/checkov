from __future__ import annotations

from abc import abstractmethod
from collections.abc import Iterable
from typing import TYPE_CHECKING, Any

from checkov.common.checks.base_check import BaseCheck
from checkov.serverless.checks.service.registry import service_registry

if TYPE_CHECKING:
    from checkov.common.models.enums import CheckCategories, CheckResult


class BaseServiceCheck(BaseCheck):
    def __init__(
        self,
        name: str,
        id: str,
        categories: Iterable[CheckCategories],
        supported_entities: Iterable[str],
        guideline: str | None = None,
    ) -> None:
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_entities=supported_entities,
            block_type="serverless",
            guideline=guideline,
        )
        service_registry.register(self)

    def scan_entity_conf(self, conf: dict[str, Any], entity_type: str) -> CheckResult:
        return self.scan_service_conf(conf)

    @abstractmethod
    def scan_service_conf(self, conf: dict[str, Any]) -> CheckResult:
        raise NotImplementedError()
