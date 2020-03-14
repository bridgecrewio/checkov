from abc import abstractmethod

from checkov.terraform.checks.provider.registry import provider_registry
from checkov.common.checks.base_check import BaseCheck


class BaseProviderCheck(BaseCheck):
    def __init__(self, name, id, categories, supported_provider):
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_provider,
                         block_type="provider")
        self.supported_provider = supported_provider
        provider_registry.register(self)

    @abstractmethod
    def scan_provider_conf(self, conf):
        raise NotImplementedError()

    def scan_entity_conf(self, conf):
        return self.scan_provider_conf(conf)
