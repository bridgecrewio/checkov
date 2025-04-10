from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class LambdaXrayEnabled(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that AWS Lambda function is configured for X-Ray tracing"
        id = "CKV_AWS_116"
        supported_resources = ['awscc_lambda_function']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "tracing_config/mode"

    def get_expected_value(self):
        return "Active"


check = LambdaXrayEnabled()
