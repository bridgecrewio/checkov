from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck


class KMSKeyWildCardPrincipal(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure KMS key policy does not contain wildcard (*) principal"
        id = "CKV_AWS_33"
        supported_resources = ("AWS::KMS::Key",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "Properties/KeyPolicy/Statement/Principal"

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        properties = conf.get("Properties")
        if properties and isinstance(properties, dict):
            policy_block = properties.get("KeyPolicy")
            if policy_block and isinstance(policy_block, dict):
                statements = policy_block.get("Statement")
                if statements and isinstance(statements, list):
                    for statement in statements:
                        principal = statement.get("Principal")
                        if not principal:
                            continue
                        if statement.get("Effect") == "Deny":
                            continue

                        if isinstance(principal, dict) and "AWS" in principal:
                            # the actual principals can be under the `AWS`
                            principal = principal["AWS"]

                        if isinstance(principal, str) and principal == "*":
                            return CheckResult.FAILED
                        if isinstance(principal, list) and "*" in principal:
                            return CheckResult.FAILED

        return CheckResult.PASSED


check = KMSKeyWildCardPrincipal()
