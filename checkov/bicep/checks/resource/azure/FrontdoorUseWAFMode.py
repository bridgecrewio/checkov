from __future__ import annotations

from typing import Any, List

from checkov.bicep.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class FrontdoorUseWAFMode(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure that Azure Front Door uses WAF in \"Detection\" or \"Prevention\" modes"
        id = "CKV_AZURE_123"
        supported_resources = ['Microsoft.Network/FrontDoorWebApplicationFirewallPolicies']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        if conf.get('properties') and isinstance(conf.get('properties'), dict):
            properties = conf['properties']
            if isinstance(properties['policySettings'], dict) and properties['policySettings']:
                policy_settings = properties.get('policySettings')
                if isinstance(policy_settings.get('enabledState'), str)  \
                        and policy_settings.get('enabledState') == "Enabled":
                    return CheckResult.PASSED
        return CheckResult.FAILED

    def get_evaluated_keys(self) -> List[str]:
        return ["policySettings/[0]/enabledState"]


check = FrontdoorUseWAFMode()
