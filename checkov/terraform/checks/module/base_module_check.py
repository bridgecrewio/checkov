from abc import abstractmethod

from .typed_base_module_check import TypedBaseModuleCheck


class BaseModuleCheck(TypedBaseModuleCheck):

    def typed_scan_module_conf(self, conf, entity_type):
        return self.scan_resource_conf(conf)

    @abstractmethod
    def scan_resource_conf(self, conf):
        # TODO rename to scan_module_conf
        raise NotImplementedError()
