from typing import Dict, Any

from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class WAFACLCVE202144228(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure WAF prevents message lookup in Log4j2. See CVE-2021-44228 aka log4jshell"
        id = "CKV_AWS_192"
        supported_resources = ["AWS::WAFv2::WebACL"]
        categories = [CheckCategories.APPLICATION_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: Dict[str, Any]) -> CheckResult:
        self.evaluated_keys = ["Properties/Rules"]
        properties = conf.get("Properties")
        if properties:
            rules = properties.get("Rules") or []
            for idx_rule, rule in enumerate(rules):
                self.evaluated_keys = [f"Properties/Rules/[{idx_rule}]/Statement"]
                statement = rule.get("Statement")
                if statement:
                    self.evaluated_keys = [f"Properties/Rules/[{idx_rule}]/Statement/ManagedRuleGroupStatement"]
                    managed_group = statement.get("ManagedRuleGroupStatement")
                    if managed_group:
                        self.evaluated_keys = [
                            f"Properties/Rules/[{idx_rule}]/Statement/ManagedRuleGroupStatement/Name"
                        ]
                        if managed_group.get("Name") == "AWSManagedRulesKnownBadInputsRuleSet":
                            self.evaluated_keys.append(
                                f"Properties/Rules/[{idx_rule}]/Statement/ManagedRuleGroupStatement/ExcludedRules"
                            )
                            excluded_rules = managed_group.get("ExcludedRules") or []
                            # rule 'Log4JRCE' should not be set to count
                            for idx_excluded_rule, excluded_rule in enumerate(excluded_rules):
                                if isinstance(excluded_rule, dict) and excluded_rule.get("Name") == "Log4JRCE":
                                    self.evaluated_keys = [
                                        f"Properties/Rules/[{idx_rule}]/Statement/ManagedRuleGroupStatement/Name",
                                        f"Properties/Rules/[{idx_rule}]/Statement/ManagedRuleGroupStatement/ExcludedRules/[{idx_excluded_rule}]/Name",
                                    ]
                                    return CheckResult.FAILED

                            self.evaluated_keys.append(f"Properties/Rules/[{idx_rule}]/OverrideAction/None")
                            override_action = rule.get("OverrideAction")
                            # check for group override
                            if override_action and next(iter(override_action.keys())) != "None":
                                return CheckResult.FAILED

                            return CheckResult.PASSED

        return CheckResult.FAILED


check = WAFACLCVE202144228()
