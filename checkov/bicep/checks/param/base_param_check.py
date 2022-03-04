from __future__ import annotations

from abc import abstractmethod
from collections.abc import Iterable

from pycep.typing import ParameterAttributes

from checkov.bicep.checks.param.registry import registry
from checkov.common.checks.base_check import BaseCheck
from checkov.common.models.enums import CheckCategories, CheckResult


class BaseParamCheck(BaseCheck):
    def __init__(
        self,
        name: str,
        id: str,
        categories: "Iterable[CheckCategories]",
        supported_type: "Iterable[str]",
        guideline: str | None = None,
    ) -> None:
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_entities=supported_type,
            block_type="param",
            guideline=guideline,
        )
        self.supported_type = supported_type
        registry.register(self)

    def scan_entity_conf(self, conf: ParameterAttributes, entity_type: str) -> CheckResult:
        self.entity_type = entity_type

        return self.scan_param_conf(conf)

    @abstractmethod
    def scan_param_conf(self, conf: ParameterAttributes) -> CheckResult:
        raise NotImplementedError()
