from abc import abstractmethod

from checkov.terraform.checks.data.registry import data_registry
from checkov.common.checks.base_check import BaseCheck


class BaseDataCheck(BaseCheck):
    def __init__(self, name, id, categories, supported_data):
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_data,
                         block_type="data")
        self.supported_data = supported_data
        data_registry.register(self)

    @abstractmethod
    def scan_data_conf(self, conf):
        raise NotImplementedError()

    def scan_entity_conf(self, conf):
        return self.scan_data_conf(conf)
