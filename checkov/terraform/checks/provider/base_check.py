from abc import abstractmethod

from checkov.common.checks.base_check import BaseCheck
from checkov.common.multi_signature import multi_signature
from checkov.terraform.checks.provider.registry import provider_registry


class BaseProviderCheck(BaseCheck):
    def __init__(self, name, id, categories, supported_provider):
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_provider,
                         block_type="provider")
        self.supported_provider = supported_provider
        provider_registry.register(self)

    def scan_entity_conf(self, conf, entity_type):
        return self.scan_provider_conf(conf, entity_type)

    @multi_signature()
    @abstractmethod
    def scan_provider_conf(self, conf, provider_type):
        raise NotImplementedError()

    @classmethod
    @scan_provider_conf.add_signature(args=["self", "conf"])
    def _scan_provider_conf_self_conf(cls, wrapped):
        def wrapper(self, conf, provider_type=None):
            # keep default argument for entity_type so old code, that doesn't set it, will work.
            return wrapped(self, conf)

        return wrapper
