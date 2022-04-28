from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories

class VPCSecurityGroupRuleAllowAll(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure security group rule is not allow-all."
        id = "CKV_YC_20"
        categories = [CheckCategories.GENERAL_SECURITY]
        supported_resources = ["yandex_vpc_security_group_rule"]
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_resources=supported_resources,
        )

    def scan_resource_conf(self, conf):
        if conf['direction'][0] == 'ingress':
            cidr_block = conf['v4_cidr_blocks']
            for cidr in cidr_block[0]:
                if cidr == "0.0.0.0/0":
                    if 'port' in conf.keys():
                        if conf['port'][0] == -1:
                            return CheckResult.FAILED
                        return CheckResult.PASSED
                    if 'from_port' not in conf.keys() and 'to_port' not in conf.keys():
                        return CheckResult.FAILED
                    if conf['from_port'][0] == 0 and conf['to_port'][0] == 65535:
                        return CheckResult.FAILED
        return CheckResult.PASSED

scanner = VPCSecurityGroupRuleAllowAll()