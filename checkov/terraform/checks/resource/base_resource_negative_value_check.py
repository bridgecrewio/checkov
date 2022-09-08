from abc import abstractmethod
from collections.abc import Iterable
from typing import List, Dict, Any, Optional

import dpath

from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.util.type_forcers import force_list
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.terraform.graph_builder.utils import get_referenced_vertices_in_value
from checkov.terraform.parser_functions import handle_dynamic_values


class BaseResourceNegativeValueCheck(BaseResourceCheck):
    def __init__(
        self,
        name: str,
        id: str,
        categories: "Iterable[CheckCategories]",
        supported_resources: "Iterable[str]",
        missing_attribute_result: CheckResult = CheckResult.PASSED,
    ) -> None:
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)
        self.missing_attribute_result = missing_attribute_result

    def scan_resource_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        handle_dynamic_values(conf)

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
            if value is None or (isinstance(value, list) and not value):
                return self.missing_attribute_result
            if get_referenced_vertices_in_value(value=value, aliases={}, resources_types=[]):
                # we don't provide resources_types as we want to stay provider agnostic
                return CheckResult.UNKNOWN
            # value can still be a list
            if isinstance(value, list):
                for val in value:
                    if val in bad_values:
                        return CheckResult.FAILED
            if value in bad_values or ANY_VALUE in bad_values:
                return CheckResult.FAILED
            else:
                return CheckResult.PASSED

        return self.missing_attribute_result

    @abstractmethod
    def get_inspected_key(self) -> str:
        """
        :return: JSONPath syntax path of the checked attribute
        """
        raise NotImplementedError()

    @abstractmethod
    def get_forbidden_values(self) -> List[Any]:
        """
        Returns a list of vulnerable values for the inspected key, governed by provider best practices
        """
        raise NotImplementedError()

    def get_excluded_key(self) -> Optional[str]:
        """
        :return: JSONPath syntax path of the an attribute that provides exclusion condition for the inspected key
        """
        return None

    def check_excluded_condition(self, value: str) -> bool:
        """
        :param:  value: value for  excluded_key
        :return: True if the value should exclude the check from failing if the inspected key has a bad value
        """
        return False

    def get_evaluated_keys(self) -> List[str]:
        return force_list(self.get_inspected_key())
