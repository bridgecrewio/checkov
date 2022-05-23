from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck
from checkov.common.models.enums import CheckCategories


class LambdaFunctionURLAuth(BaseResourceNegativeValueCheck):

    def __init__(self):
        name = "Ensure that lambda URL functions AuthType is not None"
        id = "CKV_AWS_258"
        supported_resources = ['aws_lambda_function_url']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "authorization_type"

    def get_forbidden_values(self):
        return ["NONE"]


check = LambdaFunctionURLAuth()
