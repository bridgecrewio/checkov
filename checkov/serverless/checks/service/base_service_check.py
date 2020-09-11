from abc import abstractmethod

from checkov.common.checks.base_check import BaseCheck
from checkov.serverless.checks.service.registry import service_registry


class BaseServiceCheck(BaseCheck):
    def __init__(self, name, id, categories, supported_entities):
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_entities,
                         block_type="serverless")
        service_registry.register(self)

    def scan_entity_conf(self, conf, entity_type):
        return self.scan_service_conf(conf)

    @abstractmethod
    def scan_service_conf(self, conf):
        raise NotImplementedError()
