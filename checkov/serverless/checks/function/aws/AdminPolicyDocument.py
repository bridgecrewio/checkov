from __future__ import annotations

from typing import Any

from checkov.serverless.checks.function.base_function_check import BaseFunctionCheck
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.serverless.parsers.parser import IAM_ROLE_STATEMENTS_TOKEN


class AdminPolicyDocument(BaseFunctionCheck):
    def __init__(self) -> None:
        name = "Ensure IAM policies that allow full \"*-*\" administrative privileges are not created"
        id = "CKV_AWS_1"
        supported_entities = ('serverless_aws',)
        categories = (CheckCategories.IAM,)
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_entities)

    def scan_function_conf(self, conf: dict[str, Any]) -> CheckResult:
        """
        validates iam policy document
        https://learn.hashicorp.com/terraform/aws/iam-policy
        :param conf: aws_kms_key configuration
        :return: <CheckResult>
        """
        statements = conf.get(IAM_ROLE_STATEMENTS_TOKEN)
        if statements and isinstance(statements, list):
            for statement in statements:
                if 'Action' in statement and statement.get('Effect') == 'Allow' and '*' in statement['Action'] \
                        and '*' in statement['Resource']:
                    return CheckResult.FAILED
        return CheckResult.PASSED


check = AdminPolicyDocument()
