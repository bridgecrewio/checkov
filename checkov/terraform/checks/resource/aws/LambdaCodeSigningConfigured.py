from checkov.common.models.consts import ANY_VALUE
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class LambdaCodeSigningConfigured(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that AWS Lambda function is configured for a code-signing with signing profiles, which define the trusted publishers for this function"
        id = "CKV_AWS_272"
        supported_resources = ['aws_lambda_function']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "code_signing_config_arn"

    def get_expected_value(self):
        return ANY_VALUE


check = LambdaCodeSigningConfigured()
