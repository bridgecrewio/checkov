from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class ECRPolicy(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure ECR policy is not set to public"
        id = "CKV_AWS_32"
        supported_resources = ("aws_ecr_repository_policy",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        """
            Looks for public * policy for ecr repository:
            https://www.terraform.io/docs/providers/aws/r/ecr_repository_policy.html
        :param conf: aws_ecr_repository configuration
        :return: <CheckResult>
        """
        if "policy" in conf.keys():
            policy = conf["policy"][0]
            if isinstance(policy, str):
                return CheckResult.PASSED

            statement = policy["Statement"][0]
            if statement and isinstance(statement, dict):
                principal = statement.get("Principal")
                if principal and isinstance(principal, str) and principal == "*" and not self.check_for_constrained_condition(statement):
                    self.evaluated_keys = ["policy/Statement/Principal"]
                    return CheckResult.FAILED
        return CheckResult.PASSED

    def get_evaluated_keys(self) -> list[str]:
        return ["policy"]

    def check_for_constrained_condition(self, statement: dict[str, Any]) -> bool:
        """
        Checks to see if there is a constraint on a wildcarded principal
        :param statement: statement from aws_repository_configuration
        :return: True if there is a constraint
        """
        if "Condition" in statement and isinstance(statement["Condition"], dict):
            condition = statement["Condition"]
            string_equals = None
            if "StringEquals" in condition:
                string_equals = condition["StringEquals"]
            elif "ForAllValues:StringEquals" in condition:
                string_equals = condition["ForAllValues:StringEquals"]
            elif "ForAnyValue:StringEquals" in condition:
                string_equals = condition["ForAnyValue:StringEquals"]

            if isinstance(string_equals, dict) and "aws:PrincipalOrgID" in string_equals:
                return True

        return False


check = ECRPolicy()
