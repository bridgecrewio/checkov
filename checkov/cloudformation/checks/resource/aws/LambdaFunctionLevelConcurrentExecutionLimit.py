from typing import Any

from checkov.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckCategories


class LambdaFunctionLevelConcurrentExecutionLimit(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that AWS Lambda function is configured for function-level concurrent execution limit"
        id = "CKV_AWS_115"
        supported_resources = ("AWS::Lambda::Function", "AWS::Serverless::Function")
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "Properties/ReservedConcurrentExecutions"

    def get_expected_value(self) -> Any:
        return ANY_VALUE


check = LambdaFunctionLevelConcurrentExecutionLimit()
