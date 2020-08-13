from abc import abstractmethod

from .typed_base_spec_check import TypedBaseK8Check


class BaseK8Check(TypedBaseK8Check):
    def typed_scan_spec_conf(self, conf, entity_type):
        return self.scan_spec_conf(conf)

    @abstractmethod
    def scan_spec_conf(self, conf):
        raise NotImplementedError()
