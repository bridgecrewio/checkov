from abc import abstractmethod

from checkov.common.checks.base_check import BaseCheck
from checkov.terraform.checks.data.registry import data_registry


class TypedBaseDataCheck(BaseCheck):
    def __init__(self, name, id, categories, supported_data):
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_data,
                         block_type="data")
        self.supported_data = supported_data
        data_registry.register(self)

    @abstractmethod
    def typed_scan_data_conf(self, conf, entity_type):
        raise NotImplementedError()

    def scan_entity_conf(self, conf, entity_type):
        return self.typed_scan_data_conf(conf, entity_type)
