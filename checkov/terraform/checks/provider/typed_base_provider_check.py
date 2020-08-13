from abc import abstractmethod

from checkov.terraform.checks.provider.registry import provider_registry
from checkov.common.checks.base_check import BaseCheck


class TypedBaseProviderCheck(BaseCheck):
    def __init__(self, name, id, categories, supported_provider):
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_provider,
                         block_type="provider")
        self.supported_provider = supported_provider
        provider_registry.register(self)

    @abstractmethod
    def typed_scan_provider_conf(self, conf, entity_type):
        raise NotImplementedError()

    def scan_entity_conf(self, conf, entity_type):
        return self.typed_scan_provider_conf(conf, entity_type)
