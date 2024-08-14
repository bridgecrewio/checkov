from typing import Any

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.consts import ANY_VALUE


class BedrockAgentEncrypted(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure Bedrock Agent is encrypted with a CMK"
        id = "CKV_AWS_373"
        supported_resources = ("aws_bedrockagent_agent",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "customer_encryption_key_arn"

    def get_expected_value(self) -> Any:
        return ANY_VALUE


check = BedrockAgentEncrypted()
