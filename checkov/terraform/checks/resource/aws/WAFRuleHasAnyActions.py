from __future__ import annotations

from typing import Any, List

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class WAFRuleHasAnyActions(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure WAF rule has any actions"
        id = "CKV_AWS_342"
        supported_resources = ('aws_waf_web_acl', 'aws_wafregional_web_acl', 'aws_wafv2_web_acl',
                               'aws_wafv2_rule_group', 'aws_wafregional_rule_group', 'aws_waf_rule_group')
        categories = (CheckCategories.APPLICATION_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        rules = None
        if conf.get("rule") and isinstance(conf["rule"], list):
            rules = conf["rule"]
        # don't blame me I didn't name one rule and the other rules and the other activated_rule
        elif conf.get("rules") and isinstance(conf["rules"], list):
            rules = conf["rules"]
        elif conf.get("activated_rule") and isinstance(conf["activated_rule"], list):
            rules = conf["activated_rule"]

        if isinstance(rules, list):
            for rule in rules:
                passing = False
                if "action" in rule and rule['action'] != [{}]:
                    passing = True
                if "override_action" in rule and rule['override_action'] != [{}]:
                    passing = True

                statements = rule.get('statement')
                if statements and isinstance(statements, list):
                    for statement in statements:
                        if not isinstance(statement, dict):
                            continue
                        if statement.get('managed_rule_group_statement'):
                            passing = True

                if not passing:
                    return CheckResult.FAILED

            return CheckResult.PASSED

        return CheckResult.UNKNOWN

    def get_evaluated_keys(self) -> List[str]:
        return [
            "rule",
            "rules",
            "activated_rule",
        ]


check = WAFRuleHasAnyActions()
