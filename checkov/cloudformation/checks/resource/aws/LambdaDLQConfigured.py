from typing import Any

from checkov.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckCategories


class LambdaDLQConfigured(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that AWS Lambda function is configured for a Dead Letter Queue(DLQ)"
        id = "CKV_AWS_116"
        supported_resources = ("AWS::Lambda::Function", "AWS::Serverless::Function")
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        if self.entity_type == "AWS::Lambda::Function":
            return "Properties/DeadLetterConfig/TargetArn"
        elif self.entity_type == "AWS::Serverless::Function":
            return "Properties/DeadLetterQueue/TargetArn"

        return ""

    def get_expected_value(self) -> Any:
        return ANY_VALUE


check = LambdaDLQConfigured()
