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
            self.evaluated_keys = ['ingress_security_rules']
            rules = conf.get("ingress_security_rules")
            is_list_syntax = False
            if isinstance(rules[0], list):
                # Old terraform oci provider version syntax for ingress_security_rules was a list instead of a block
                rules = rules[0]
                is_list_syntax = True
            for idx, rule in enumerate(rules):
                if 'stateless' in rule.keys():
                    stateless = rule.get("stateless")
                    if stateless != [True] and stateless is not True:
                        self.evaluated_keys = [f'ingress_security_rules/[{idx}]/stateless'] if is_list_syntax \
                            else [f'ingress_security_rules/[0]/[{idx}]/stateless']
                        return CheckResult.FAILED
            return CheckResult.PASSED

        return CheckResult.UNKNOWN


check = SecurityListIngressStateless()
