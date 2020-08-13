from abc import abstractmethod

from checkov.common.checks.base_check import BaseCheck
from checkov.kubernetes.registry import registry


class TypedBaseK8Check(BaseCheck):
    def __init__(self, name, id, categories, supported_entities):
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_entities,
                         block_type="k8")
        self.supported_specs = supported_entities
        registry.register(self)

    @abstractmethod
    def typed_scan_spec_conf(self, conf, entity_type):
        raise NotImplementedError()

    def scan_entity_conf(self, conf, entity_type):
        return self.typed_scan_spec_conf(conf, entity_type)

    @abstractmethod
    def get_resource_id(self, conf):
        pass
