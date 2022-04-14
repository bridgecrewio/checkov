from __future__ import annotations

from abc import abstractmethod
from collections.abc import Iterable
from typing import Any

from checkov.bicep.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.models.consts import ANY_VALUE
from checkov.common.util.data_structures_utils import find_in_dict


class BaseResourceValueCheck(BaseResourceCheck):
    def __init__(
        self,
        name: str,
        id: str,
        categories: "Iterable[CheckCategories]",
        supported_resources: "Iterable[str]",
        guideline: str | None = None,
        missing_block_result: CheckResult = CheckResult.FAILED,
    ) -> None:
        super().__init__(
            name=name, id=id, categories=categories, supported_resources=supported_resources, guideline=guideline
        )
        self.missing_block_result = missing_block_result

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        inspected_key = self.get_inspected_key()
        expected_values = self.get_expected_values()

        value = find_in_dict(conf, inspected_key)

        if value is None:
            return self.missing_block_result
        if ANY_VALUE in expected_values:
            return CheckResult.PASSED
        if value in expected_values:
            return CheckResult.PASSED
        # quite often string values are case-insensitive
        if isinstance(value, str) and value.lower() in [exp.lower() for exp in expected_values if isinstance(exp, str)]:
            return CheckResult.PASSED

        return self.missing_block_result

    @abstractmethod
    def get_inspected_key(self) -> str:
        """
        :return: JSONPath syntax path of the checked attribute
        """
        raise NotImplementedError()

    def get_expected_values(self) -> list[Any]:
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

    def get_evaluated_keys(self) -> list[str]:
        return [self.get_inspected_key()]
