import re
from abc import abstractmethod
from collections.abc import Iterable
from typing import List, Any, Dict

from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck
from checkov.cloudformation.context_parser import ContextParser
from checkov.cloudformation.parser import DictNode
from checkov.common.parsers.node import StrNode
from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.util.type_forcers import force_list

VARIABLE_DEPENDANT_REGEX = re.compile(r"(?:Ref)\.[^\s]+")


class BaseResourceValueCheck(BaseResourceCheck):
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

    @staticmethod
    def _filter_key_path(path: str) -> List[str]:
        """
        Filter an attribute path to contain only named attributes by dropping array indices from the path)
        :param path: valid JSONPath of an attribute
        :return: List of named attributes with respect to the input JSONPath order
        """
        regex = re.compile(r"^\[?\d+\]?$")
        return [x for x in path.split("/") if not re.search(regex, x)]

    @staticmethod
    def _is_variable_dependant(value: Any) -> bool:
        if isinstance(value, str) and re.match(VARIABLE_DEPENDANT_REGEX, value):
            return True
        return False

    @staticmethod
    def _is_nesting_key(inspected_attributes: List[str], key: str) -> bool:
        """
        Resolves whether a key is a subset of the inspected nesting attributes
        :param inspected_attributes: list of nesting attributes
        :param key: JSONPath key of an attribute
        :return: True/False
        """
        return any(x in key for x in inspected_attributes)

    def scan_resource_conf(self, conf: Dict[StrNode, DictNode]) -> CheckResult:
        inspected_key = self.get_inspected_key()
        expected_values = self.get_expected_values()
        path_elements = inspected_key.split("/")
        matches = ContextParser.search_deep_keys(path_elements[-1], conf, [])
        if len(matches) > 0:
            for match in matches:
                # CFN files are parsed differently from terraform, which causes the path search above to behave differently.
                # The tesult is path parts with integer indexes, instead of strings like '[0]'. This logic replaces
                # those, allowing inspected_keys in checks to use the same syntax.
                for i in range(0, len(match)):
                    if type(match[i]) == int:
                        match[i] = f"[{match[i]}]"

                if match[:-1] == path_elements:
                    # Inspected key exists
                    value = match[-1]
                    if ANY_VALUE in expected_values and value is not None and (not isinstance(value, str) or value):
                        # Key is found on the configuration - if it accepts any value, the check is PASSED
                        return CheckResult.PASSED
                    if isinstance(value, list) and len(value) == 1:
                        value = value[0]
                    if self._is_variable_dependant(value):
                        # If the tested attribute is variable-dependant, then result is PASSED
                        return CheckResult.PASSED
                    if value in expected_values:
                        return CheckResult.PASSED
                    return CheckResult.FAILED

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
