from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class NetworkACLUnrestricted(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure NACL ingress does not allow all Ports"
        id = "CKV_AWS_352"
        supported_resources = ('aws_network_acl_rule',)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        egress = conf.get('egress')
        if egress and isinstance(egress, list) and egress[0]:
            return CheckResult.UNKNOWN
        port = conf.get('from_port')
        if port and isinstance(port, list) and port[0]:
            return CheckResult.PASSED
        return CheckResult.FAILED


check = NetworkACLUnrestricted()
