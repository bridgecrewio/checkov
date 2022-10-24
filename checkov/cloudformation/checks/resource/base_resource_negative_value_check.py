from abc import abstractmethod
from collections.abc import Iterable
from typing import List, Any, Optional, Dict

from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck
from checkov.cloudformation.context_parser import ContextParser
from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckResult, CheckCategories


class BaseResourceNegativeValueCheck(BaseResourceCheck):
    def __init__(
        self,
        name: str,
        id: str,
        categories: "Iterable[CheckCategories]",
        supported_resources: "Iterable[str]",
        missing_block_result: CheckResult = CheckResult.FAILED,
    ) -> None:
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)
        self.missing_block_result = missing_block_result

    def scan_resource_conf(self, conf: Dict[str, Any], entity_type: str) -> CheckResult:
        excluded_key = self.get_excluded_key()
        if excluded_key is not None:
            path_elements = excluded_key.split("/")
            matches = ContextParser.search_deep_keys(path_elements[-1], conf, [])
            if len(matches) > 0:
                for match in matches:
                    if match[:-1] == path_elements:
                        if isinstance(match, list) and len(match) == 1:
                            match = match[0]
                        if self.check_excluded_condition(match):
                            return CheckResult.PASSED

        inspected_key = self.get_inspected_key()
        bad_values = self.get_forbidden_values()
        path_elements = inspected_key.split("/")
        matches = ContextParser.search_deep_keys(path_elements[-1], conf, [])
        if len(matches) > 0:
            for match in matches:
                if match[:-1] == path_elements:
                    if match[-1] in bad_values or ANY_VALUE in bad_values:
                        return CheckResult.FAILED

        return CheckResult.PASSED

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

    def check_excluded_condition(self, value: Any) -> bool:
        """
        :param:  value: value for  excluded_key
        :return: True if the value should exclude the check from failing if the inspected key has a bad value
        """
        return False

    def get_evaluated_keys(self) -> List[str]:
        return [self.get_inspected_key()]
