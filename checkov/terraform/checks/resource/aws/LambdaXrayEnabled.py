from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class LambdaXrayEnabled(BaseResourceValueCheck):
    def __init__(self):
        name = "X-ray tracing is enabled for Lambda"
        id = "CKV_AWS_50"
        supported_resources = ['aws_lambda_function']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "tracing_config/[0]/mode"

    def get_expected_value(self):
        return "PassThrough"

    def get_expected_values(self):
        return [self.get_expected_value(), "Active"]


check = LambdaXrayEnabled()
