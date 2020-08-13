from abc import abstractmethod

from checkov.common.checks.base_check import BaseCheck
from checkov.serverless.registry import sls_registry


class TypedBaseFunctionCheck(BaseCheck):
    def __init__(self, name, id, categories, supported_entities):
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_entities,
                         block_type="serverless")
        self.supported_entities = supported_entities
        sls_registry.register(self)

    @abstractmethod
    def typed_scan_function_conf(self, conf, entity_type):
        raise NotImplementedError()

    def scan_entity_conf(self, conf, entity_type):
        return self.typed_scan_function_conf(conf, entity_type)
