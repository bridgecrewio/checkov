from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class WAFRuleHasAnyActions(BaseResourceCheck):
    def __init__(self):
        name = "Ensure WAF rule has any actions"
        id = "CKV_AWS_342"
        supported_resources = ('aws_waf_web_acl', 'aws_wafregional_web_acl', 'aws_wafv2_web_acl',
                               'aws_wafv2_rule_group', 'aws_wafregional_rule_group', 'aws_waf_rule_group')
        categories = (CheckCategories.APPLICATION_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        rules = None
        if conf.get("rule") and isinstance(conf["rule"], list):
            rules = conf["rule"]
        # dont blame me i didn't name one rule and the other rules and the other activated_rule
        elif conf.get("rules") and isinstance(conf["rules"], list):
            rules = conf["rules"]
        elif conf.get("activated_rule") and isinstance(conf["activated_rule"], list):
            rules = conf["activated_rule"]

        if isinstance(rules, list):
            for rule in rules:
                if "action" in rule and rule['action'] != [{}]:
                    continue
                if "override_action" in rule and rule['override_action'] != [{}]:
                    continue
                return CheckResult.FAILED
            return CheckResult.PASSED

        return CheckResult.UNKNOWN


check = WAFRuleHasAnyActions()
