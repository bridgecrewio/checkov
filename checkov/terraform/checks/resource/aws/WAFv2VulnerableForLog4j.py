from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class WAFv2VulnerableForLog4j(BaseResourceCheck):

    def __init__(self):
        name = "Ensure WAFv2 WebACL is configured with AMR for Log4j Vulnerability"
        id = "CKV_AWS_387"
        supported_resources = ['aws_wafv2_web_acl']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        badInput = False
        ipList = False
        rules = conf.get("rule", [])
        if not isinstance(rules, list):
            rules = [rules]

        for rule_block in rules:
            if isinstance(rule_block, dict):
                statements = rule_block.get("statement", [])
                if not isinstance(statements, list):
                    statements = [statements]
                for stmt in statements:
                    if isinstance(stmt, dict):
                        if 'managed_rule_group_statement' in stmt:
                            if stmt['managed_rule_group_statement'][0]['name']:
                                if stmt['managed_rule_group_statement'][0]['name'][0] == "AWSManagedRulesCommonRuleSet":
                                    badInput = True
                                elif stmt['managed_rule_group_statement'][0]['name'][0] == "AWSManagedRulesAnonymousIpList":
                                    ipList = True
        if badInput and ipList:
            return CheckResult.PASSED
        return CheckResult.FAILED


check = WAFv2VulnerableForLog4j()
