from typing import Dict, Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.common.util.type_forcers import force_list
from checkov.arm.base_resource_check import BaseResourceCheck


class FrontDoorWAFACLCVE202144228(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure Front Door WAF prevents message lookup in Log4j2. See CVE-2021-44228 aka log4jshell"
        id = "CKV_AZURE_133"
        supported_resources = ["Microsoft.Network/frontdoorWebApplicationFirewallPolicies"]
        categories = [CheckCategories.APPLICATION_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: Dict[Any, Any]) -> CheckResult:
        self.evaluatedKeys = ["managedRules"]
        properties = conf.get("properties")
        if properties is None or "managedRules" not in properties:
            return CheckResult.FAILED

        managedRules = properties.get("managedRules")
        if not managedRules:
            return CheckResult.FAILED

        for idx_managed_rule, managed_rule in enumerate(force_list(managedRules.get("managedRuleSets", []))):
            self.evaluated_keys = [f"managedRules/[{idx_managed_rule}]/type"]
            if managed_rule and managed_rule.get("ruleSetType") in ["DefaultRuleSet", "Microsoft_DefaultRuleSet"]:
                ruleOverrides = managed_rule.get("ruleGroupOverrides", [])
                if ruleOverrides == []:
                    return CheckResult.PASSED
                for idx_override, rule_override in enumerate(force_list(ruleOverrides)):
                    self.evaluated_keys.append(
                        f"managedRules/[{idx_managed_rule}]/ruleGroupOverrides/[{idx_override}]/ruleGroupName"
                    )
                    if rule_override.get("ruleGroupName") == "JAVA":
                        rules = rule_override.get("rules", [])
                        for idx_rule, rule in enumerate(force_list(rules)):
                            self.evaluated_keys.extend([
                                f"managedRules/[{idx_managed_rule}]/ruleGroupOverrides/[{idx_override}]/rules/[{idx_rule}]/ruleId",
                                f"managedRules/[{idx_managed_rule}]/ruleGroupOverrides/[{idx_override}]/rules/[{idx_rule}]/enabledState",
                                f"managedRules/[{idx_managed_rule}]/ruleGroupOverrides/[{idx_override}]/rules/[{idx_rule}]/action",
                            ])
                            if rule.get("ruleId") == "944240":
                                enabledState = rule.get("enabledState")
                                if not enabledState:
                                    return CheckResult.FAILED
                                if rule.get("action") in ["Block", "Redirect"]:
                                    return CheckResult.PASSED

        return CheckResult.FAILED


check = FrontDoorWAFACLCVE202144228()
