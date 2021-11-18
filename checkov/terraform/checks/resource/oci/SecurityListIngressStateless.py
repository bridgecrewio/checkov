from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class SecurityListIngressStateless(BaseResourceCheck):
    def __init__(self):
        name = "Ensure VCN inbound security lists are stateless"
        id = "CKV_OCI_17"
        supported_resources = ['oci_core_security_list']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'ingress_security_rules' in conf.keys():
            rules = conf.get("ingress_security_rules")
            for rule in rules:
                if 'stateless' in rule.keys():
                    if rule.get("stateless") == [True]:
                        return CheckResult.PASSED
                    else:
                        return CheckResult.FAILED
            return CheckResult.PASSED

        return CheckResult.SKIPPED


check = SecurityListIngressStateless()
