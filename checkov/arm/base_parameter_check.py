from __future__ import annotations

from abc import abstractmethod
from collections.abc import Iterable
from typing import TYPE_CHECKING, Any

from checkov.arm.registry import arm_parameter_registry
from checkov.common.checks.base_check import BaseCheck

if TYPE_CHECKING:
    from checkov.common.models.enums import CheckCategories, CheckResult


class BaseParameterCheck(BaseCheck):
    def __init__(
        self,
        name: str,
        id: str,
        categories: Iterable[CheckCategories],
        supported_resources: Iterable[str],
        guideline: str | None = None,
    ) -> None:
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_entities=supported_resources,
            block_type="parameter",
            guideline=guideline,
        )
        self.supported_resources = supported_resources
        arm_parameter_registry.register(self)

    def scan_entity_conf(self, conf: dict[str, Any], entity_type: str) -> CheckResult:
        self.entity_type = entity_type

        return self.scan_resource_conf(conf)

    @abstractmethod
    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        raise NotImplementedError()
