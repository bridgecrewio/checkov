from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class LambdaFunctionLevelConcurrentExecutionLimit(BaseResourceCheck):
    def __init__(self):
        name = "Ensure that AWS Lambda function is configured for function-level concurrent execution limit"
        id = "CKV_AWS_115"
        supported_resources = ['aws_lambda_function']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        key = 'reserved_concurrent_executions'
        if key not in conf.keys() or conf.get(key)[0] == '${-1}':
            return CheckResult.FAILED
        return CheckResult.PASSED


check = LambdaFunctionLevelConcurrentExecutionLimit()
