from checkov.common.models.consts import ANY_VALUE
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class LambdaDLQConfigured(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that AWS Lambda function is configured for a Dead Letter Queue(DLQ)"
        id = "CKV_AWS_116"
        supported_resources = ['aws_lambda_function']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "dead_letter_config/[0]/target_arn"

    def get_expected_value(self):
        return ANY_VALUE


check = LambdaDLQConfigured()
