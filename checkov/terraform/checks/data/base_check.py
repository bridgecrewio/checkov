from __future__ import annotations

from abc import abstractmethod
from collections.abc import Iterable
from typing import Dict, List, Any

from checkov.common.checks.base_check import BaseCheck
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.data.registry import data_registry


class BaseDataCheck(BaseCheck):
    def __init__(
        self,
        name: str,
        id: str,
        categories: Iterable[CheckCategories],
        supported_data: Iterable[str],
        guideline: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_data,
                         block_type="data", guideline=guideline)
        self.supported_data = supported_data
        data_registry.register(self)

    def scan_entity_conf(self, conf: Dict[str, List[Any]], entity_type: str) -> CheckResult:
        self.entity_type = entity_type

        if conf.get("count") == [0]:
            return CheckResult.UNKNOWN

        return self.scan_data_conf(conf)

    @abstractmethod
    def scan_data_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        raise NotImplementedError()
