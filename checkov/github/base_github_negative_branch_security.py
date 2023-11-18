from __future__ import annotations

from typing import Any
from abc import abstractmethod

from bc_jsonpath_ng import parse

from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.github.base_github_configuration_check import BaseGithubCheck
from checkov.github.schemas.branch_protection import schema as branch_security_schema
from checkov.github.schemas.no_branch_protection import schema as no_branch_security_schema
from checkov.json_doc.enums import BlockType

MESSAGE_BRANCH_NOT_PROTECTED = "Branch not protected"


class NegativeBranchSecurity(BaseGithubCheck):
    def __init__(self, id: str, name: str, missing_attribute_result: CheckResult = CheckResult.PASSED) -> None:
        categories = (CheckCategories.SUPPLY_CHAIN,)
        super().__init__(
            id=id,
            name=name,
            categories=categories,
            supported_entities=("*",),
            block_type=BlockType.DOCUMENT,
        )
        self.missing_attribute_result = missing_attribute_result

    def scan_entity_conf(self, conf: dict[str, Any], entity_type: str) -> CheckResult:
        if branch_security_schema.validate(conf):
            evaluated_key = self.get_evaluated_keys()[0].replace("/", ".")
            jsonpath_expression = parse(f"$..{evaluated_key}")
            matches = jsonpath_expression.find(conf)
            if not matches:
                # attribute doesn't exists
                return self.missing_attribute_result

            if matches:
                forbidden_values = self.get_forbidden_values()
                if ANY_VALUE in forbidden_values or any(
                    match.value in forbidden_values for match in matches
                ):
                    # attribute exists, but is not a value of 'get_forbidden_values()' or 'ANY_VALUE'
                    return CheckResult.FAILED

            return CheckResult.PASSED
        if no_branch_security_schema.validate(conf):
            message = conf.get("message", "")
            if message == MESSAGE_BRANCH_NOT_PROTECTED:
                return CheckResult.FAILED
        return CheckResult.UNKNOWN

    @abstractmethod
    def get_evaluated_keys(self) -> list[str]:
        """List of JSONPath syntax path of the checked attributes"""
        pass

    @abstractmethod
    def get_forbidden_values(self) -> list[Any]:
        """List of forbidden values for the evaluated keys"""
        pass
