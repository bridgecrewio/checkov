from typing import Any

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.consts import ANY_VALUE


class BedrockGuardrails(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure AWS Bedrock agent is associated with Bedrock guardrails"
        id = "CKV_AWS_383"
        supported_resources = ("aws_bedrockagent_agent",)
        categories = (CheckCategories.AI_AND_ML,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "guardrail_configuration/[0]/guardrail_identifier"

    def get_expected_value(self) -> Any:
        return ANY_VALUE


check = BedrockGuardrails()
