from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck

class LambdaXrayEnabled(BaseResourceCheck):
    def __init__(self):
        name = "X-ray tracing is enabled for Lambda"
        id = "CKV_AWS_50"
        supported_resources = ['aws_lambda_function']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if "tracing_config" in conf.keys():
            return CheckResult.PASSED
        return CheckResult.FAILED


check = LambdaXrayEnabled()
