import re
from abc import abstractmethod
from collections.abc import Iterable
from typing import Dict, Any, List, Optional

from checkov.arm.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.models.consts import ANY_VALUE
from checkov.common.util.data_structures_utils import find_in_dict

VARIABLE_DEPENDANT_REGEX = re.compile(r"(?:local|var|module)\.[^\s]+")


class BaseResourceValueCheck(BaseResourceCheck):
    def __init__(
        self,
        name: str,
        id: str,
        categories: List[CheckCategories],
        supported_resources: "Iterable[str]",
        missing_block_result: CheckResult = CheckResult.FAILED,
        guideline: Optional[str] = None,
    ) -> None:
        super().__init__(
            name=name, id=id, categories=categories, supported_resources=supported_resources, guideline=guideline
        )
        self.missing_block_result = missing_block_result

    @staticmethod
    def _is_variable_dependant(value: Any) -> bool:
        if isinstance(value, str) and re.match(VARIABLE_DEPENDANT_REGEX, value):
            return True
        return False

    def scan_resource_conf(self, conf: Dict[str, Any]) -> CheckResult:
        inspected_key = self.get_inspected_key()
        expected_values = self.get_expected_values()
        value = find_in_dict(conf, inspected_key)
        if value:
            if ANY_VALUE in expected_values:
                # Key is found in the configuration - if it accepts any value, the check is PASSED
                return CheckResult.PASSED
            if isinstance(value, list) and len(value) == 1:
                value = value[0]
            if value in expected_values:
                return CheckResult.PASSED
            if self._is_variable_dependant(value):
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
