from abc import abstractmethod
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class BaseResourceNegativeValueCheck(BaseResourceCheck):
    def __init__(self, name, id, categories, supported_resources):
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        raise NotImplementedError()

    @abstractmethod
    def get_inspected_key(self):
        """
        :return: JSONPath syntax path of the checked attribute
        """
        raise NotImplementedError()

    def get_vulnerable_values(self):
        """
        Returns the vulnerable value for the inspected, governed by provider best practices
        """
        return []

    def get_excluded_key(self):
        """
        :return: JSONPath syntax path of the an attribute that provides exclusion condition for the inspected key
        """
        return None

    def get_excluded_condition(self):
        """
        Returns the excluded value for the excluded key, which states the vulnerable value is valid for it
        """
        def check_condition(value):
            return self.get_excluded_key() is not None
        return check_condition

