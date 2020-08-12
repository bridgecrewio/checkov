from abc import abstractmethod

from checkov.common.checks.base_check import BaseCheck
from checkov.terraform.checks.module.registry import module_registry


class BaseModuleCheck(BaseCheck):
    def __init__(self, name, id, categories, supported_resources):
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_resources,
                         block_type="module")
        self.supported_resources = supported_resources
        module_registry.register(self)

    @abstractmethod
    def scan_resource_conf(self, conf):
        raise NotImplementedError()

    def scan_entity_conf(self, conf):
        return self.scan_resource_conf(conf)
