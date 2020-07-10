from abc import abstractmethod

import dpath
from checkov.common.models.enums import CheckResult
from checkov.kubernetes.base_spec_check import BaseK8Check


class BaseSpecOmittedOrValueCheck(BaseK8Check):
    def __init__(self, name, id, categories, supported_entities):
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_entities)

    def scan_spec_conf(self, conf):
        inspected_key = self.get_inspected_key()
        if dpath.util.search(conf, inspected_key,yielded=False) != {}:
            if dpath.util.get(conf, inspected_key) != self.get_expected_value():
                return CheckResult.FAILED
        return CheckResult.PASSED

    @abstractmethod
    def get_inspected_key(self):
        raise NotImplemented()

    def get_expected_value(self):
        # default expected value. can be override by derived class
        return False
