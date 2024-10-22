from __future__ import annotations

from typing import List, Any

from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckCategories, CheckResult


class LambdaServicePermission(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure that AWS Lambda function permissions delegated to AWS services are limited by SourceArn or SourceAccount"
        id = "CKV_AWS_364"
        supported_resources = ("AWS::Lambda::Permission",)
        categories = (CheckCategories.IAM,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        properties = conf.get('Properties')
        if properties and isinstance(properties, dict):
            principal = properties.get('Principal')
            if principal and isinstance(principal, str):
                principal_parts = principal.split('.')
                try:
                    if principal_parts[1] == 'amazonaws' and principal_parts[2] == 'com':
                        if properties.get('SourceArn') or properties.get('SourceAccount'):
                            return CheckResult.PASSED
                        else:
                            return CheckResult.FAILED
                except IndexError:
                    # Not a service principal, so pass.
                    return CheckResult.UNKNOWN
        return CheckResult.UNKNOWN

    def get_evaluated_keys(self) -> List[str]:
        return ['Properties/Principal', 'Properties/SourceArn', 'Properties/SourceAccount']


check = LambdaServicePermission()
