from typing import Any, List

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class BedrockAgentCoreBrowserNetworkMode(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure Bedrock AgentCore browser is not configured with PUBLIC network mode"
        id = "CKV_AWS_396"
        supported_resources = ("aws_bedrockagentcore_browser",)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "network_configuration/[0]/network_mode"

    def get_expected_values(self) -> List[Any]:
        return ["VPC"]


check = BedrockAgentCoreBrowserNetworkMode()
