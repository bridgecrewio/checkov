from abc import abstractmethod
from typing import List, Dict, Any

from checkov.common.checks.base_check import BaseCheck
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.provider.registry import provider_registry


class BaseProviderCheck(BaseCheck):
    def __init__(self, name: str, id: str, categories: List[CheckCategories], supported_provider: List[str]) -> None:
        super().__init__(
            name=name, id=id, categories=categories, supported_entities=supported_provider, block_type="provider"
        )
        self.supported_provider = supported_provider
        provider_registry.register(self)

    def scan_entity_conf(self, conf: Dict[str, List[Any]], entity_type: str) -> CheckResult:
        return self.scan_provider_conf(conf)

    @abstractmethod
    def scan_provider_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        raise NotImplementedError()
