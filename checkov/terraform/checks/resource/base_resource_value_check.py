from abc import abstractmethod
from typing import List, Dict, Any

import dpath.util
import re
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.models.consts import ANY_VALUE
from checkov.common.util.type_forcers import force_list
from checkov.terraform.graph_builder.utils import get_referenced_vertices_in_value
from checkov.terraform.parser_functions import handle_dynamic_values
from checkov.terraform.parser_utils import find_var_blocks



class BaseResourceValueCheck(BaseResourceCheck):
    def __init__(
        self,
        name: str,
        id: str,
        categories: List[CheckCategories],
        supported_resources: List[str],
        missing_block_result: CheckResult = CheckResult.FAILED,
    ) -> None:
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)
        self.missing_block_result = missing_block_result

    @staticmethod
    def _filter_key_path(path: str) -> List[str]:
        """
        Filter an attribute path to contain only named attributes by dropping array indices from the path)
        :param path: valid JSONPath of an attribute
        :return: List of named attributes with respect to the input JSONPath order
        """
        return [x for x in path.split("/") if not re.search(re.compile(r"^\[?\d+]?$"), x)]

    @staticmethod
    def _is_variable_dependant(value: Any) -> bool:
        if not isinstance(value, str):
            return False
        if "${" not in value:
            return False

        if find_var_blocks(value):
            return True
        return False

    @staticmethod
    def _is_nesting_key(inspected_attributes: List[str], key: List[str]) -> bool:
        """
        Resolves whether a key is a subset of the inspected nesting attributes
        :param inspected_attributes: list of nesting attributes
        :param key: JSONPath key of an attribute
        :return: True/False
        """
        return any(x in key for x in inspected_attributes)

    def scan_resource_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        handle_dynamic_values(conf)
        inspected_key = self.get_inspected_key()
        expected_values = self.get_expected_values()
        if dpath.search(conf, inspected_key) != {}:
            # Inspected key exists
            value = dpath.get(conf, inspected_key)
            if isinstance(value, list) and len(value) == 1:
                value = value[0]
            if ANY_VALUE in expected_values and value is not None and (not isinstance(value, str) or value):
                # Key is found on the configuration - if it accepts any value, the check is PASSED
                return CheckResult.PASSED
            if self._is_variable_dependant(value):
                # If the tested attribute is variable-dependant, then result is PASSED
                return CheckResult.PASSED
            if value in expected_values:
                return CheckResult.PASSED
            if get_referenced_vertices_in_value(value=value, aliases={}, resources_types=[]):
                # we don't provide resources_types as we want to stay provider agnostic
                return CheckResult.UNKNOWN
            return CheckResult.FAILED
        else:
            # Look for the configuration in a bottom-up fashion
            inspected_attributes = self._filter_key_path(inspected_key)
            for attribute in reversed(inspected_attributes):
                for sub_key, sub_conf in dpath.search(conf, f"**/{attribute}", yielded=True):
                    filtered_sub_key = self._filter_key_path(sub_key)
                    # Only proceed with check if full path for key is similar - not partial match
                    if inspected_attributes == filtered_sub_key:
                        if self._is_nesting_key(inspected_attributes, filtered_sub_key):
                            if isinstance(sub_conf, list) and len(sub_conf) == 1:
                                sub_conf = sub_conf[0]
                            if sub_conf in self.get_expected_values():
                                return CheckResult.PASSED
                            if self._is_variable_dependant(sub_conf):
                                # If the tested attribute is variable-dependant, then result is PASSED
                                return CheckResult.PASSED

        return self.missing_block_result

    @abstractmethod
    def get_inspected_key(self) -> str:
        """
        :return: JSONPath syntax path of the checked attribute
        """
        raise NotImplementedError()

    def get_expected_values(self) -> List[Any]:
        """
        Override the method with the list of acceptable values if the check has more than one possible expected value, given
        the inspected key
        :return: List of expected values, defaults to a list of the expected value
        """
        return [self.get_expected_value()]

    def get_expected_value(self) -> Any:
        """
        Returns the default expected value, governed by provider best practices
        """
        return True

    def get_evaluated_keys(self) -> List[str]:
        return force_list(self.get_inspected_key())
