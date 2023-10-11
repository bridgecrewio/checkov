from __future__ import annotations

from typing import List, Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class LambdaServicePermission(BaseResourceCheck):
    def __init__(self) -> None:
        description = "Ensure that AWS Lambda function permissions delegated to AWS services are limited by SourceArn or SourceAccount"
        id = "CKV_AWS_364"
        supported_resources = ('aws_lambda_permission',)
        categories = (CheckCategories.IAM,)
        super().__init__(name=description, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        # Replace this with the custom logic for your check
        principal = conf.get("principal")
        if principal and isinstance(principal, list) and isinstance(principal[0], str):
            principal_parts = principal[0].split('.')
            try:
                if principal_parts[1] == 'amazonaws' and principal_parts[2] == 'com':  # This confirms that the principal is set as a service principal.
                    if 'source_arn' in conf or 'source_account' in conf:  # If either of these are set, we're good and the check should pass.
                        self.evaluated_keys = self.get_evaluated_keys()
                        return CheckResult.PASSED
                    else:
                        self.evaluated_keys = self.get_evaluated_keys()
                        return CheckResult.FAILED
            except IndexError:
                return CheckResult.UNKNOWN
        return CheckResult.UNKNOWN

    def get_evaluated_keys(self) -> List[str]:
        return ["principal", "source_arn", "source_account"]


check = LambdaServicePermission()
