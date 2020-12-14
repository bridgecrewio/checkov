from abc import abstractmethod

from checkov.common.checks.base_check import BaseCheck
from checkov.common.multi_signature import multi_signature
from checkov.kubernetes.registry import registry


class BaseK8Check(BaseCheck):
    def __init__(self, name, id, categories, supported_entities):
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_entities,
                         block_type="k8")
        self.supported_specs = supported_entities
        registry.register(self)

    @abstractmethod
    def get_resource_id(self, conf):
        pass

    def scan_entity_conf(self, conf, entity_type):
        return self.scan_spec_conf(conf, entity_type)

    @multi_signature()
    @abstractmethod
    def scan_spec_conf(self, conf, entity_type):
        raise NotImplementedError()

    @classmethod
    @scan_spec_conf.add_signature(args=["self", "conf"])
    def _scan_spec_conf_self_conf(cls, wrapped):
        def wrapper(self, conf, entity_type=None):
            # keep default argument for entity_type so old code, that doesn't set it, will work.
            return wrapped(self, conf)

        return wrapper
