from abc import abstractmethod

from checkov.common.checks.base_check import BaseCheck
from checkov.common.multi_signature import multi_signature
from checkov.terraform.checks.module.registry import module_registry


class BaseModuleCheck(BaseCheck):
    def __init__(self, name, id, categories, supported_resources):
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_resources,
                         block_type="module")
        self.supported_resources = supported_resources
        module_registry.register(self)

    def scan_entity_conf(self, conf, entity_type):
        return self.scan_module_conf(conf, entity_type)

    @abstractmethod
    @multi_signature()
    def scan_module_conf(self, conf, entity_type):
        raise NotImplementedError()

    @classmethod
    @scan_module_conf.add_signature(args=["self", "conf"])
    def _scan_module_conf_self_conf(cls, wrapped):
        def wrapper(self, conf, entity_type=None):
            # keep default argument for entity_type so old code, that doesn't set it, will work.
            return wrapped(self, conf)

        return wrapper
