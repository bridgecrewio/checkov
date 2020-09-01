from abc import abstractmethod

from checkov.common.checks.base_check import BaseCheck
from checkov.terraform.checks.provider.registry import provider_registry


class BaseProviderCheck(BaseCheck):
    def __init__(self, name, id, categories, supported_provider):
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_provider,
                         block_type="provider")
        self.supported_provider = supported_provider
        provider_registry.register(self)

    def scan_entity_conf(self, conf, entity_type):
        # entity_type is always 'provider'
        return self.scan_provider_conf(conf)

    @abstractmethod
    def scan_provider_conf(self, conf):
        raise NotImplementedError()
