from typing import Dict, Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.common.util.type_forcers import force_list
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class AppGatewayWAFACLCVE202144228(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure Application Gateway WAF prevents message lookup in Log4j2. See CVE-2021-44228 aka log4jshell"
        id = "CKV_AZURE_135"
        supported_resources = ("azurerm_web_application_firewall_policy",)
        categories = (CheckCategories.APPLICATION_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: Dict[str, Any]) -> CheckResult:
        self.evaluated_keys = ["managed_rules"]
        managed_rules = conf.get("managed_rules")
        if managed_rules:
            managed_rule_sets = managed_rules[0].get("managed_rule_set") or []
            for idx_rule_set, rule_set in enumerate(force_list(managed_rule_sets)):
                self.evaluated_keys = [
                    f"managed_rules/[0]/managed_rule_set[{idx_rule_set}]/type",
                    f"managed_rules/[0]/managed_rule_set[{idx_rule_set}]/version",
                ]
                if rule_set.get("type", ["OWASP"]) == ["OWASP"] and rule_set.get("version") in (["3.1"], ["3.2"]):
                    rule_overrides = rule_set.get("rule_group_override") or []
                    for idx_override, rule_override in enumerate(force_list(rule_overrides)):
                        self.evaluated_keys.extend(
                            [
                                f"managed_rules/[0]/managed_rule_set[{idx_rule_set}]/rule_group_override/[{idx_override}]/rule_group_name",
                                f"managed_rules/[0]/managed_rule_set[{idx_rule_set}]/rule_group_override/[{idx_override}]/disabled_rules",
                            ]
                        )
                        if rule_override.get("rule_group_name") == ["REQUEST-944-APPLICATION-ATTACK-JAVA"]:
                            disabled_rules = rule_override.get("disabled_rules") or []
                            if isinstance(disabled_rules, list) and "944240" in force_list(disabled_rules[0]):
                                return CheckResult.FAILED

                    return CheckResult.PASSED

        return CheckResult.FAILED


check = AppGatewayWAFACLCVE202144228()
