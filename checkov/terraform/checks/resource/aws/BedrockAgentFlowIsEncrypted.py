from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class BedrockAgentFlowIsEncrypted(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure Bedrock Agent Flow is encrypted with a KMS key"
        id = "CKV_AWS_394"
        supported_resources = ("aws_bedrockagent_flow",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        if conf.get("customer_encryption_key_arn"):
            return CheckResult.PASSED
        return CheckResult.FAILED

    def get_evaluated_keys(self) -> list[str]:
        return ["customer_encryption_key_arn"]


check = BedrockAgentFlowIsEncrypted()
