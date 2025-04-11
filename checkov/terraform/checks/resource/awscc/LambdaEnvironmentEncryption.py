from typing import Any

from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class LambdaEnvironmentEncryption(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure Lambda function environment variables are encrypted"
        id = "CKV_AWS_173"
        supported_resources = ("awscc_lambda_function",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "kms_key_arn"

    def get_expected_value(self) -> Any:
        return ANY_VALUE


check = LambdaEnvironmentEncryption()
