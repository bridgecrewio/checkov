from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class NACLPortCheck(BaseResourceCheck):
    def __init__(self):
        name = "An ingress Network ACL rule should not allow ALL ports."
        id = "CKV_NCP_77"
        supported_resources = ['ncloud_network_acl_rule']

        categories = [CheckCategories.NETWORKING]
        guideline = "You should Ensure Network ACL rule doesn't open All ports."
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources, guideline=guideline)

    def scan_resource_conf(self, conf):
        if 'inbound' in conf.keys():
            for inbound in conf['inbound']:
                if 'port_range' in inbound.keys():
                    for port_range in inbound['port_range']:
                        if port_range == "1-65535":
                            return CheckResult.FAILED
                    return CheckResult.PASSED
        return CheckResult.FAILED

check = NACLPortCheck()
