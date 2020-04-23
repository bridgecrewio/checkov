from abc import abstractmethod

from checkov.common.checks.base_check import BaseCheck
from checkov.kubernetes.registry import registry


class BaseK8Check(BaseCheck):
    def __init__(self, name, id, categories, supported_entities):
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_entities,
                         block_type="k8")
        self.supported_specs = supported_entities
        registry.register(self)

    @abstractmethod
    def scan_spec_conf(self, conf):
        raise NotImplementedError()

    def scan_entity_conf(self, conf):
        return self.scan_spec_conf(conf)

    @abstractmethod
    def get_resource_id(self, conf):
        pass
