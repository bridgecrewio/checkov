from abc import abstractmethod

from checkov.common.checks.base_check import BaseCheck
from checkov.serverless.registry import sls_registry


class BaseFunctionCheck(BaseCheck):
    def __init__(self, name, id, categories, supported_entities):
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_entities,
                         block_type="serverless")
        self.supported_entities = supported_entities
        sls_registry.register(self)

    @abstractmethod
    def scan_function_conf(self, conf):
        raise NotImplementedError()

    def scan_entity_conf(self, conf):
        return self.scan_function_conf(conf)
