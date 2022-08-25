from __future__ import annotations

from abc import abstractmethod
from typing import Any, TYPE_CHECKING

import dpath
from checkov.common.models.enums import CheckResult
from checkov.kubernetes.checks.resource.base_spec_check import BaseK8Check

if TYPE_CHECKING:
    from checkov.common.models.enums import CheckCategories
    from collections.abc import Iterable


class BaseSpecOmittedOrValueCheck(BaseK8Check):
    def __init__(
        self, name: str, id: str, categories: Iterable[CheckCategories], supported_entities: Iterable[str]
    ) -> None:
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_entities)

    def scan_spec_conf(self, conf: dict[str, Any]) -> CheckResult:
        inspected_key = self.get_inspected_key()
        if dpath.util.search(conf, inspected_key, yielded=False) != {}:
            if dpath.util.get(conf, inspected_key) != self.get_expected_value():
                return CheckResult.FAILED
        return CheckResult.PASSED

    @abstractmethod
    def get_inspected_key(self) -> str:
        raise NotImplementedError()

    def get_expected_value(self) -> Any:
        # default expected value. can be override by derived class
        return False
