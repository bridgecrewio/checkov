from typing import List

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import \
    BaseResourceCheck


class VPCSecurityGroupRuleSet(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Tencent Cloud VPC security group rules do not accept all traffic"
        id = "CKV_TC_8"
        supported_resources = ['tencentcloud_security_group_rule_set']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf) -> CheckResult:
        if conf.get("ingress"):
            for i in conf["ingress"]:
                if i.get("action") and i["action"][0] != "ACCEPT":
                    continue
                if i.get("cidr_block") is None and i.get("ipv6_cidr_block") is None:
                    continue
                if i.get("cidr_block") and i["cidr_block"][0] != "0.0.0.0/0":
                    continue
                if i.get("ipv6_cidr_block") and (i["ipv6_cidr_block"][0] not in ["::/0", "0::0/0"]):
                    continue
                return CheckResult.FAILED

        return CheckResult.PASSED

    def get_evaluated_keys(self) -> List[str]:
        return ["ingress"]


check = VPCSecurityGroupRuleSet()
