from abc import abstractmethod

from .typed_base_provider_check import TypedBaseProviderCheck


class BaseProviderCheck(TypedBaseProviderCheck):
    def typed_scan_provider_conf(self, conf, entity_type):
        return self.scan_provider_conf(conf)

    @abstractmethod
    def scan_provider_conf(self, conf):
        raise NotImplementedError()
