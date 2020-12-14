from abc import abstractmethod

from checkov.common.checks.base_check import BaseCheck
from checkov.terraform.checks.module.registry import module_registry


class BaseModuleCheck(BaseCheck):
    def __init__(self, name, id, categories, supported_resources=None):
        """
        Base class for terraform module call related checks.

        :param name: an error message that is shown, when the check failed.
        :param id: the id of the check
        :param categories: categories of the check
        :param supported_resources: DEPRECATED the resources that this check applies to.

            This is deprecated because there is only one resource type that is valid for
            checks that extend this class.
        """
        if supported_resources is None:
            supported_resources = ['module']
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_resources,
                         block_type="module")
        self.supported_resources = supported_resources
        module_registry.register(self)

    def scan_entity_conf(self, conf, entity_type):
        # entity_type is always 'module'
        return self.scan_module_conf(conf)

    @abstractmethod
    def scan_module_conf(self, conf):
        raise NotImplementedError()
