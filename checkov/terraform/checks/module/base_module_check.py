from abc import abstractmethod

from .typed_base_module_check import TypedBaseModuleCheck


class BaseModuleCheck(TypedBaseModuleCheck):

    def typed_scan_module_conf(self, conf, entity_type):
        return self.scan_module_conf(conf)

    @abstractmethod
    def scan_module_conf(self, conf):
        raise NotImplementedError()
