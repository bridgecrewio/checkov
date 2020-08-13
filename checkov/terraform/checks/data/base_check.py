from abc import abstractmethod

from .typed_base_data_check import TypedBaseDataCheck


class BaseDataCheck(TypedBaseDataCheck):

    def typed_scan_data_conf(self, conf, entity_type):
        return self.scan_data_conf(conf)

    @abstractmethod
    def scan_data_conf(self, conf):
        raise NotImplementedError()
