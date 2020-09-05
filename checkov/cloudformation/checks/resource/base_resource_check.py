from abc import abstractmethod

from checkov.cloudformation.checks.resource.registry import cfn_registry
from checkov.common.checks.base_check import BaseCheck
from checkov.common.multi_signature import multi_signature


class BaseResourceCheck(BaseCheck):
    def __init__(self, name, id, categories, supported_resources):
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_resources,
                         block_type="resource")
        self.supported_resources = supported_resources
        cfn_registry.register(self)

    def scan_entity_conf(self, conf, entity_type):
        return self.scan_resource_conf(conf, entity_type)

    @multi_signature()
    @abstractmethod
    def scan_resource_conf(self, conf, entity_type):
        raise NotImplementedError()

    @classmethod
    @scan_resource_conf.add_signature(args=["self", "conf"])
    def _scan_resource_conf_self_conf(cls, wrapped):
        def wrapper(self, conf, entity_type=None):
            # keep default argument for entity_type so old code, that doesn't set it, will work.
            return wrapped(self, conf)

        return wrapper
