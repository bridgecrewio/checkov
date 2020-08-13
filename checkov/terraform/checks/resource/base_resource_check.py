from abc import abstractmethod

from .typed_base_resource_check import TypedBaseResourceCheck


class BaseResourceCheck(TypedBaseResourceCheck):
    def typed_scan_resource_conf(self, conf, entity_type):
        return self.scan_resource_conf(conf)

    @abstractmethod
    def scan_resource_conf(self, conf):
        raise NotImplementedError()
