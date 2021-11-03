from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class WAFHasAnyRules(BaseResourceCheck):
    def __init__(self):
        name = "Ensure WAF has any rules"
        id = "CKV_AWS_175"
        supported_resources = ['aws_waf_web_acl', 'aws_wafv2_web_acl']
        categories = [CheckCategories.APPLICATION_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if "rules" not in conf.keys() and "rule" not in conf.keys():
            return CheckResult.FAILED
        if "rules" in conf.keys() and conf["rules"] == [{}]:
            return CheckResult.FAILED
        if "rule" in conf.keys() and conf["rule"] == [{}]:
            return CheckResult.FAILED
        return CheckResult.PASSED


check = WAFHasAnyRules()
