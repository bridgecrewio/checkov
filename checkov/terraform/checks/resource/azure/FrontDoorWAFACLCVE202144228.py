from typing import Dict, Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.common.util.type_forcers import force_list
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class FrontDoorWAFACLCVE202144228(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure Front Door WAF prevents message lookup in Log4j2. See CVE-2021-44228 aka log4jshell"
        id = "CKV_AZURE_133"
        supported_resources = ["azurerm_frontdoor_firewall_policy"]
        categories = [CheckCategories.APPLICATION_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: Dict[str, Any]) -> CheckResult:
        self.evaluated_keys = ["managed_rule"]
        managed_rules = conf.get("managed_rule") or []
        for idx_managed_rule, managed_rule in enumerate(force_list(managed_rules)):
            self.evaluated_keys = [f"managed_rule/[{idx_managed_rule}]/type"]
            if managed_rule.get("type") in (["DefaultRuleSet"], ["Microsoft_DefaultRuleSet"]):
                rule_overrides = managed_rule.get("override") or []
                for idx_override, rule_override in enumerate(force_list(rule_overrides)):
                    self.evaluated_keys.append(
                        f"managed_rule/[{idx_managed_rule}]/override/[{idx_override}]/rule_group_name"
                    )
                    if rule_override.get("rule_group_name") == ["JAVA"]:
                        rules = rule_override.get("rule") or []
                        for idx_rule, rule in enumerate(force_list(rules)):
                            self.evaluated_keys.extend(
                                [
                                    f"managed_rule/[{idx_managed_rule}]/override/[{idx_override}]/rule/[{idx_rule}]/rule_id",
                                    f"managed_rule/[{idx_managed_rule}]/override/[{idx_override}]/rule/[{idx_rule}]/enabled",
                                    f"managed_rule/[{idx_managed_rule}]/override/[{idx_override}]/rule/[{idx_rule}]/action",
                                ]
                            )
                            if rule.get("rule_id") == ["944240"]:
                                if rule.get("enabled") != [True]:
                                    return CheckResult.FAILED
                                if rule.get("action") not in (["Block"], ["Redirect"]):
                                    return CheckResult.FAILED

                return CheckResult.PASSED

        return CheckResult.FAILED


check = FrontDoorWAFACLCVE202144228()
