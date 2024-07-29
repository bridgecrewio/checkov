from typing import Dict, Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.common.util.type_forcers import force_list
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class WAFACLCVE202144228(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure WAF prevents message lookup in Log4j2. See CVE-2021-44228 aka log4jshell"
        id = "CKV_AWS_192"
        supported_resources = ["aws_wafv2_web_acl"]
        categories = [CheckCategories.APPLICATION_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: Dict[str, Any]) -> CheckResult:
        self.evaluated_keys = ["rule"]
        rules = conf.get("rule") or []
        for idx_rule, rule in enumerate(force_list(rules)):
            self.evaluated_keys = [f"rule/[{idx_rule}]/statement"]
            statement = rule.get("statement")
            if statement:
                self.evaluated_keys = [f"rule/[{idx_rule}]/statement/[0]/managed_rule_group_statement"]
                if not isinstance(statement, list) or not isinstance(statement[0], dict):
                    return CheckResult.UNKNOWN
                managed_group = statement[0].get("managed_rule_group_statement")
                if managed_group:
                    self.evaluated_keys = [f"rule/[{idx_rule}]/statement/[0]/managed_rule_group_statement/[0]/name"]
                    if managed_group[0] and managed_group[0].get("name") == ["AWSManagedRulesKnownBadInputsRuleSet"]:
                        self.evaluated_keys.append(
                            f"rule/[{idx_rule}]/statement/[0]/managed_rule_group_statement/[0]/excluded_rule"
                        )
                        excluded_rules = managed_group[0].get("excluded_rule") or []
                        # rule 'Log4JRCE' should not be set to count
                        for idx_excluded_rule, excluded_rule in enumerate(force_list(excluded_rules)):
                            if excluded_rule and excluded_rule.get("name") == ["Log4JRCE"]:
                                self.evaluated_keys = [
                                    f"rule/[{idx_rule}]/statement/[0]/managed_rule_group_statement/[0]/name",
                                    f"rule/[{idx_rule}]/statement/[0]/managed_rule_group_statement/[0]/excluded_rule/[{idx_excluded_rule}]/name",
                                ]
                                return CheckResult.FAILED

                        self.evaluated_keys.append(
                            f"rule/[{idx_rule}]/override_action/[0]/none"
                        )
                        override_action = rule.get("override_action")
                        # check for group override
                        override_action_none = override_action[0].get("none")
                        # Terraform plan includes both keys, but one is a dict and the not chosen one a list
                        if not override_action_none or not isinstance(override_action_none[0], dict):
                            return CheckResult.FAILED

                        return CheckResult.PASSED

        return CheckResult.FAILED


check = WAFACLCVE202144228()
