from abc import abstractmethod

import dpath

from checkov.terraform.models.enums import CheckResult

from checkov.terraform.checks.resource.base_check import BaseResourceCheck

expected_value = True


class BaseResourceBooleanValueCheck(BaseResourceCheck):
    def __init__(self, name, id, categories, supported_resources):
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        inspected_key = self.get_inspected_key()
        if dpath.util.search(conf, inspected_key) != {}:
            if dpath.util.get(conf, inspected_key)[0] == expected_value:
                return CheckResult.PASSED
        return CheckResult.FAILED

    @abstractmethod
    def get_inspected_key(self):
        raise NotImplemented()
