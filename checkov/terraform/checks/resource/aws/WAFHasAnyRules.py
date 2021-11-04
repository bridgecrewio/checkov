from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class WAFHasAnyRules(BaseResourceCheck):
    def __init__(self):
        name = "Ensure WAF has associated rules"
        id = "CKV_AWS_175"
        supported_resources = ['aws_waf_web_acl', 'aws_wafregional_web_acl', 'aws_wafv2_web_acl']
        categories = [CheckCategories.APPLICATION_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if "rules" in conf.keys() and conf["rules"] != [{}]:
            return CheckResult.PASSED
        if "rule" in conf.keys() and conf["rule"] != [{}]:
            return CheckResult.PASSED
        return CheckResult.FAILED


check = WAFHasAnyRules()
