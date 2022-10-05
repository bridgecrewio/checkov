from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class ACGIngressCheck(BaseResourceCheck):
    def __init__(self):
        name = "An ingress security group rule allows traffic from /0"
        id = "CKV_NCP_6"
        supported_resources = ['ncloud_access_control_group_rule']

        categories = [CheckCategories.NETWORKING]
        guideline = "You should restrict access to IP addresses or ranges that explicitly require it where possible."
        super().__init__(name=name, id=id, categories=categories,
                         supported_resources=supported_resources, guideline=guideline)

    def scan_resource_conf(self, conf):
        if 'inbound' in conf.keys():
            for inbound in conf['inbound']:
                ip = inbound.get('ip_block', '0.0.0.0/0')[0]
                if ip == '0.0.0.0/0' or ip == '::/0':
                    return CheckResult.FAILED
        return CheckResult.PASSED

check = ACGIngressCheck()