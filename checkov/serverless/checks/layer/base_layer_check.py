from abc import abstractmethod

from checkov.common.checks.base_check import BaseCheck
from checkov.serverless.checks.layer.registry import layer_registry


class BaseLayerCheck(BaseCheck):
    def __init__(self, name, id, categories, supported_entities, guideline=None):
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_entities,
                         block_type="serverless", guideline=guideline)
        layer_registry.register(self)

    def scan_entity_conf(self, conf, entity_type):
        return self.scan_layer_conf(conf)

    @abstractmethod
    def scan_layer_conf(self, conf):
        raise NotImplementedError()
