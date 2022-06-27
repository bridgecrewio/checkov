from abc import abstractmethod

from pycep.typing import ParameterAttributes
from typing_extensions import NotRequired

from checkov.arm.registry import arm_parameter_registry
from checkov.common.checks.base_check import BaseCheck
from checkov.common.multi_signature import multi_signature


class CheckovParameterAttributes(ParameterAttributes):
    CKV_AZURE_131_secret: NotRequired[str]


class BaseParameterCheck(BaseCheck):
    def __init__(self, name, id, categories, supported_resources, guideline=None):
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_resources,
                         block_type="parameter", guideline=guideline)
        self.supported_resources = supported_resources
        arm_parameter_registry.register(self)

    def scan_entity_conf(self, conf: CheckovParameterAttributes, entity_type):
        return self.scan_resource_conf(conf, entity_type)

    @multi_signature()
    @abstractmethod
    def scan_resource_conf(self, conf: CheckovParameterAttributes, entity_type):
        raise NotImplementedError()

    @classmethod
    @scan_resource_conf.add_signature(args=["self", "conf"])
    def _scan_resource_conf_self_conf(cls, wrapped):
        def wrapper(self, conf, entity_type=None):
            # keep default argument for entity_type so old code, that doesn't set it, will work.
            return wrapped(self, conf)

        return wrapper
