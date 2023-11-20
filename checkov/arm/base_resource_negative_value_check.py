from __future__ import annotations

import re
from abc import abstractmethod
from collections.abc import Iterable
from typing import Any

from checkov.arm.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.models.consts import ANY_VALUE
from checkov.common.util.data_structures_utils import find_in_dict
from checkov.common.util.type_forcers import force_list

VARIABLE_DEPENDANT_REGEX = re.compile(r"(?:parameters|variables)\(")


class BaseResourceNegativeValueCheck(BaseResourceCheck):
    def __init__(
        self,
        name: str,
        id: str,
        categories: "Iterable[CheckCategories]",
        supported_resources: "Iterable[str]",
        missing_block_result: CheckResult = CheckResult.PASSED,
        guideline: str | None = None,
    ) -> None:
        super().__init__(
            name=name, id=id, categories=categories, supported_resources=supported_resources, guideline=guideline
        )
        self.missing_block_result = missing_block_result

    @staticmethod
    def _is_variable_dependant(value: Any) -> bool:
        return bool(isinstance(value, str) and re.match(VARIABLE_DEPENDANT_REGEX, value))

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        inspected_key = self.get_inspected_key()
        forbidden_values = self.get_forbidden_values()
        value = find_in_dict(conf, inspected_key)
        if value:
            if isinstance(value, list) and len(value) == 1:
                value = value[0]

            if self._is_variable_dependant(value):
                # If the tested attribute is variable-dependant, then result is PASSED
                return CheckResult.UNKNOWN

            if value in forbidden_values or ANY_VALUE in forbidden_values:
                return CheckResult.FAILED
            else:
                return CheckResult.PASSED

        return self.missing_block_result

    @abstractmethod
    def get_inspected_key(self) -> str:
        """
        :return: JSONPath syntax path of the checked attribute
        """
        raise NotImplementedError()

    @abstractmethod
    def get_forbidden_values(self) -> list[Any]:
        """
        Returns a list of vulnerable values for the inspected key, governed by provider best practices
        """
        raise NotImplementedError()

    def get_evaluated_keys(self) -> list[str]:
        return force_list(self.get_inspected_key())
