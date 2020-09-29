from abc import abstractmethod

from checkov.common.checks.base_check import BaseCheck
from checkov.serverless.checks.plugin.registry import plugin_registry


class BasePluginCheck(BaseCheck):
    def __init__(self, name, id, categories, supported_entities):
        super().__init__(name=name, id=id, categories=categories,
                         supported_entities=supported_entities,
                         block_type="serverless")
        plugin_registry.register(self)

    def scan_entity_conf(self, conf, entity_type):
        return self.scan_plugin_list(conf)

    @abstractmethod
    def scan_plugin_list(self, plugin_list):
        raise NotImplementedError()
