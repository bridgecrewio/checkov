from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import \
    BaseResourceCheck


class VPCSecurityGroupRuleSet(BaseResourceCheck):
    def __init__(self):
        name = "Ensure VPC security group rule not accept all traffic"
        id = "CKV_TC_8"
        supported_resources = ['tencentcloud_security_group_rule_set']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf) -> CheckResult:
        if conf.get("ingress"):
             for i in conf["ingress"]:
                  if i.get("action") and i["action"][0] != "ACCEPT":
                       continue
                  if  i.get("cidr_block") and i["cidr_block"][0] != "0.0.0.0/0":
                       continue
                  if  i.get("protocol") and i["protocol"][0] != "ALL":
                       continue
                  if  i.get("port") and i["port"][0] != "ALL":
                       continue
                  return CheckResult.FAILED
                
        return CheckResult.PASSED

check = VPCSecurityGroupRuleSet()
