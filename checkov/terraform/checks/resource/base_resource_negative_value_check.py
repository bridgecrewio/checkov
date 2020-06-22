from abc import abstractmethod

import dpath

from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class BaseResourceNegativeValueCheck(BaseResourceCheck):
    def __init__(self, name, id, categories, supported_resources):
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        excluded_key = self.get_excluded_key()
        if excluded_key is not None:
            if dpath.search(conf, excluded_key) != {}:
                value = dpath.get(conf, excluded_key)
                if isinstance(value, list) and len(value) == 1:
                    value = value[0]
                if self.check_excluded_condition(value):
                    return CheckResult.PASSED

        inspected_key = self.get_inspected_key()
        bad_values = self.get_forbidden_values()
        if dpath.search(conf, inspected_key) != {}:
            value = dpath.get(conf, inspected_key)
            if isinstance(value, list) and len(value) == 1:
                value = value[0]
            if value in bad_values or ANY_VALUE in bad_values:
                return CheckResult.FAILED

        return CheckResult.PASSED

    @abstractmethod
    def get_inspected_key(self):
        """
        :return: JSONPath syntax path of the checked attribute
        """
        raise NotImplementedError()

    @abstractmethod
    def get_forbidden_values(self):
        """
        Returns a list of vulnerable values for the inspected key, governed by provider best practices
        """
        raise NotImplementedError()

    def get_excluded_key(self):
        """
        :return: JSONPath syntax path of the an attribute that provides exclusion condition for the inspected key
        """
        return None

    def check_excluded_condition(self, value):
        """
        :param:  value: value for  excluded_key
        :return: True if the value should exclude the check from failing if the inspected key has a bad value
        """
        return False

