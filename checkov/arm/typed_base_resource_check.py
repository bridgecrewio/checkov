from abc import abstractmethod

from checkov.arm.registry import arm_registry
from checkov.common.checks.base_check import BaseCheck


class TypedBaseResourceCheck(BaseCheck):
    def __init__(self, name, id, categories, supported_resources):
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_resources,
                         block_type="resource")
        self.supported_resources = supported_resources
        arm_registry.register(self)

    @abstractmethod
    def typed_scan_resource_conf(self, conf, entity_type):
        raise NotImplementedError()

    def scan_entity_conf(self, conf, entity_type):
        return self.typed_scan_resource_conf(conf, entity_type)
