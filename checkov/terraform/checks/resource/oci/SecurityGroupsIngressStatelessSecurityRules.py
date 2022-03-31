from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class SecurityGroupsIngressStatelessSecurityRules(BaseResourceCheck):
    def __init__(self):
        name = "Ensure security groups has stateless ingress security rules"
        id = "CKV_OCI_20"
        supported_resources = ['oci_core_network_security_group_security_rule']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        stateless = conf.get('stateless')
        direction = conf.get('direction')
        if direction[0] == 'INGRESS':
            if stateless is None or stateless[0] is False:
                return CheckResult.FAILED
            return CheckResult.PASSED
        return CheckResult.SKIPPED


check = SecurityGroupsIngressStatelessSecurityRules()
