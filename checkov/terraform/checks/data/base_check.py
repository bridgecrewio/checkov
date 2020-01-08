from abc import abstractmethod

from checkov.terraform.checks.data.registry import data_registry
from checkov.terraform.checks.utilities.base_check import BaseCheck


class BaseDataCheck(BaseCheck):
    def __init__(self, name, id, categories, supported_data):
        self.supported_data = supported_data
        data_registry.register(self)
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_data,
                         block_type="data")

    @abstractmethod
    def scan_data_conf(self, conf):
        raise NotImplementedError()

    def scan_entity_conf(self, conf):
        return self.scan_data_conf(conf)
