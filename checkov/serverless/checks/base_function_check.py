from abc import abstractmethod

from .typed_base_function_check import TypedBaseFunctionCheck


class BaseFunctionCheck(TypedBaseFunctionCheck):

    def typed_scan_function_conf(self, conf, entity_type):
        return self.scan_function_conf(conf)

    @abstractmethod
    def scan_function_conf(self, conf):
        raise NotImplementedError()
