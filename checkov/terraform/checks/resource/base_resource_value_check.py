from abc import abstractmethod

import dpath

from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult


class BaseResourceValueCheck(BaseResourceCheck):
    def __init__(self, name, id, categories, supported_resources):
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        inspected_key = self.get_inspected_key()
        if dpath.util.search(conf, inspected_key) != {}:
            if dpath.util.get(conf, inspected_key)[0] == self.get_expected_value():
                return CheckResult.PASSED
        return CheckResult.FAILED

    @abstractmethod
    def get_inspected_key(self):
        raise NotImplemented()

    def get_expected_value(self):
        # default expected value. can be override by derived class
        return True
