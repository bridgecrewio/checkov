from typing import Dict, Any
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.arm.base_resource_check import BaseResourceCheck
from checkov.common.util.type_forcers import force_list


class AppGatewayWAFACLCVE202144228(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure Application Gateway WAF prevents message lookup in Log4j2. See CVE-2021-44228 aka log4jshell"
        id = "CKV_AZURE_135"
        supported_resources = ("Microsoft.Network/ApplicationGatewayWebApplicationFirewallPolicies",)
        categories = (CheckCategories.APPLICATION_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,)

    def scan_resource_conf(self, conf: Dict[str, Any]) -> CheckResult:
        properties = conf.get("properties")
        if not properties:
            return CheckResult.FAILED
        self.evaluated_keys = properties.get("managedRules")
        managed_rules = properties.get("managedRules")
        if managed_rules:
            managed_rule_sets = managed_rules.get("managedRuleSets") or []
            for idx_rule_set, rule_set in enumerate(force_list(managed_rule_sets)):
                self.evaluated_keys = [
                    f"managedRules/[0]/managedRuleSets[{idx_rule_set}]/ruleSetType",
                    f"managedRules/[0]/managedRuleSets[{idx_rule_set}]/ruleSetVersion",
                ]
                if (rule_set.get("ruleSetType") == "OWASP" or not rule_set.get("ruleSetType")) and rule_set.get("ruleSetVersion") in ["3.1", "3.2"]:
                    rule_overrides = rule_set.get("ruleGroupOverrides") or []
                    for idx_override, rule_override in enumerate(force_list(rule_overrides)):
                        self.evaluated_keys.extend(
                            [
                                f"managedRules/[0]/managedRuleSets[{idx_rule_set}]/ruleGroupOverrides/[{idx_override}]/ruleGroupName",
                                f"managedRules/[0]/managedRuleSets[{idx_rule_set}]/ruleGroupOverrides/[{idx_override}]/rules",
                            ]
                        )
                        if isinstance(rule_override, dict) and rule_override.get("ruleGroupName") == "REQUEST-944-APPLICATION-ATTACK-JAVA":
                            disabled_rules = rule_override.get("rules") or []
                            for idx_rule_id, disabled_rule in enumerate(force_list(disabled_rules)):
                                self.evaluated_keys.extend(
                                    [
                                        f"managedRules/[0]/managedRuleSets[{idx_rule_set}]/ruleGroupOverrides/[{idx_override}]/rules/[{idx_rule_id}]/ruleId",
                                    ]
                                )
                                if disabled_rule.get("ruleId") == "944240":
                                    return CheckResult.FAILED

                    return CheckResult.PASSED

        return CheckResult.FAILED


check = AppGatewayWAFACLCVE202144228()
