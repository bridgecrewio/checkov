from abc import abstractmethod
from typing import Dict, List, Callable, Optional, Any

from checkov.common.checks.base_check import BaseCheck
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.multi_signature import multi_signature
from checkov.terraform.checks.data.registry import data_registry


class BaseDataCheck(BaseCheck):
    def __init__(self, name: str, id: str, categories: List[CheckCategories], supported_data: List[str]) -> None:
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_data, block_type="data")
        self.supported_data = supported_data
        data_registry.register(self)

    def scan_entity_conf(self, conf: Dict[str, List[Any]], entity_type: str) -> CheckResult:
        if conf.get("count") == [0]:
            return CheckResult.UNKNOWN

        return self.scan_data_conf(conf, entity_type)

    @multi_signature()
    @abstractmethod
    def scan_data_conf(self, conf: Dict[str, List[Any]], entity_type: str) -> CheckResult:
        raise NotImplementedError()

    @classmethod
    @scan_data_conf.add_signature(args=["self", "conf"])
    def _scan_data_conf_self_conf(cls, wrapped: Callable[..., CheckResult]) -> Callable[..., CheckResult]:
        def wrapper(
            self: "BaseDataCheck", conf: Dict[str, List[Any]], entity_type: Optional[str] = None
        ) -> CheckResult:
            # keep default argument for entity_type so old code, that doesn't set it, will work.
            return wrapped(self, conf)

        return wrapper
