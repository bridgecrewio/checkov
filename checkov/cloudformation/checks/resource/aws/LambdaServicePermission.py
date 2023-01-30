from typing import List

from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckCategories, CheckResult


class LambdaPermission(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure that AWS Lambda function permissions delegated to AWS services are limited by SourceArn or SourceAccount"
        id = "CKV_AWS_286"
        supported_resources = ["AWS::Lambda::Permission"]
        categories = [CheckCategories.GENERAL_SECURITY, ]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        properties = conf.get('Properties')
        if properties is not None:
            principal = properties.get('Principal')
            if 'amazonaws.com' in principal:
                if properties.get('SourceArn') or properties.get('SourceAccount'):
                    return CheckResult.PASSED
                else:
                    return CheckResult.FAILED
        return CheckResult.PASSED

    def get_evaluated_keys(self) -> List[str]:
        return ['Properties/Principal', 'Properties/SourceArn', 'Properties/SourceAccount']


check = LambdaPermission()