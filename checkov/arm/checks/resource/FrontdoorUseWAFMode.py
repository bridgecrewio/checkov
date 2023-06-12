from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.arm.base_resource_check import BaseResourceCheck


class FrontdoorUseWAFMode(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure that Azure Front Door uses WAF in \"Detection\" or \"Prevention\" modes"
        id = "CKV_AZURE_123"
        supported_resources = ('Microsoft.Network/FrontDoorWebApplicationFirewallPolicies',)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        properties = conf.get('properties')
        if properties and isinstance(properties, dict):
            policy_settings = properties.get('policySettings')
            if policy_settings and isinstance(policy_settings, dict):
                if policy_settings.get('enabledState') == "Enabled":
                    return CheckResult.PASSED
        return CheckResult.FAILED

    def get_evaluated_keys(self) -> list[str]:
        return ["policySettings/[0]/enabledState"]


check = FrontdoorUseWAFMode()
