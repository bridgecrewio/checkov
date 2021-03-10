from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class LambdaInVPC(BaseResourceValueCheck):

    def __init__(self):
        name = "Ensure that AWS Lambda function is configured inside a VPC"
        id = "CKV_AWS_117"
        supported_resources = ['aws_lambda_function']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "vpc_config"

    def get_expected_value(self):
        return ANY_VALUE


check = LambdaInVPC()
