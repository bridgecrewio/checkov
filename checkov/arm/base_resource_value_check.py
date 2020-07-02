from abc import abstractmethod
import dpath.util
import re
from checkov.arm.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult
from checkov.common.models.consts import ANY_VALUE

VARIABLE_DEPENDANT_REGEX = r'(?:local|var)\.[^\s]+'


class BaseResourceValueCheck(BaseResourceCheck):
    def __init__(self, name, id, categories, supported_resources):
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    @staticmethod
    def _filter_key_path(path):
        """
        Filter an attribute path to contain only named attributes by dropping array indices from the path)
        :param path: valid JSONPath of an attribute
        :return: List of named attributes with respect to the input JSONPath order
        """
        return [x for x in path.split("/") if not re.search(r'^\[?\d+\]?$', x)]

    @staticmethod
    def _is_variable_dependant(value):
        if isinstance(value, str) and re.match(VARIABLE_DEPENDANT_REGEX, value):
            return True
        return False

    @staticmethod
    def _is_nesting_key(inspected_attributes, key):
        """
        Resolves whether a key is a subset of the inspected nesting attributes
        :param inspected_attributes: list of nesting attributes
        :param key: JSONPath key of an attribute
        :return: True/False
        """
        return any([x in key for x in inspected_attributes])

    def scan_resource_conf(self, conf):
        inspected_key = self.get_inspected_key()
        expected_values = self.get_expected_values()
        if dpath.search(conf, inspected_key) != {}:
            if ANY_VALUE in expected_values:
                # Key is found on the configuration - if it accepts any value, the check is PASSED
                return CheckResult.PASSED
            value = dpath.get(conf, inspected_key)
            if isinstance(value, list) and len(value) == 1:
                value = value[0]
            if self._is_variable_dependant(value):
                # If the tested attribute is variable-dependant, then result is PASSED
                return CheckResult.PASSED
            if value in expected_values:
                return CheckResult.PASSED
        else:
            # Look for the configuration in a bottom-up fashion
            inspected_attributes = self._filter_key_path(inspected_key)
            for attribute in reversed(inspected_attributes):
                for sub_key, sub_conf in dpath.search(conf, f'**/{attribute}', yielded=True):
                    filtered_sub_key = self._filter_key_path(sub_key)
                    if self._is_nesting_key(inspected_attributes, filtered_sub_key):
                        if isinstance(sub_conf, list) and len(sub_conf) == 1:
                            sub_conf = sub_conf[0]
                        if sub_conf in self.get_expected_values():
                            return CheckResult.PASSED
                        if self._is_variable_dependant(sub_conf):
                            # If the tested attribute is variable-dependant, then result is PASSED
                            return CheckResult.PASSED

        return CheckResult.FAILED

    @abstractmethod
    def get_inspected_key(self):
        """
        :return: JSONPath syntax path of the checked attribute
        """
        raise NotImplementedError()

    def get_expected_values(self):
        """
        Override the method with the list of acceptable values if the check has more than one possible expected value, given
        the inspected key
        :return: List of expected values, defaults to a list of the expected value
        """
        return [self.get_expected_value()]

    def get_expected_value(self):
        """
        Returns the default expected value, governed by provider best practices
        """
        return True