from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class ACGEgressCheck(BaseResourceCheck):
    def __init__(self):
        name = "An Egress security group rule allows traffic to /0"
        id = "CKV_NCP_11"
        supported_resources = ['ncloud_access_control_group_rule']

        categories = [CheckCategories.NETWORKING]
        guideline = "You should restrict access to IP addresses or ranges that are explicitly required where possible."
        super().__init__(name=name, id=id, categories=categories,
                         supported_resources=supported_resources, guideline=guideline)

    def scan_resource_conf(self, conf):
        if 'outbound' in conf.keys():
            for inbound in conf['outbound']:
                ip = inbound.get('ip_block', '0.0.0.0/0')[0]
                if ip == '0.0.0.0/0' or ip == '::/0':
                    return CheckResult.FAILED
        return CheckResult.PASSED

check = ACGEgressCheck()