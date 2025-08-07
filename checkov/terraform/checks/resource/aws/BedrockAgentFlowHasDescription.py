from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class BedrockAgentFlowHasDescription(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure Bedrock Agent Flow has a description"
        id = "CKV_AWS_393"
        supported_resources = ("aws_bedrockagent_flow",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        if conf.get("description"):
            return CheckResult.PASSED
        return CheckResult.FAILED

    def get_evaluated_keys(self) -> list[str]:
        return ["description"]


check = BedrockAgentFlowHasDescription()
