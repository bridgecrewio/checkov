from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck

ports = (20, 21, 22, 3389)


class NetworkACLRestrictsSSH(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Network ACL restricts on sensitive ports"
        id = "CKV_AWS_228"
        supported_resources = ['aws_network_acl']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if conf.get("ingress"):
            ingress = conf.get("ingress")[0]
            for rule in ingress:
                if rule.get('cidr_block'):
                    if rule.get('cidr_block') == "0.0.0.0/0":
                        for port in ports:
                            if rule.get('from_port') >= port and rule.get('to_port') <= port:
                                return CheckResult.FAILED
            return CheckResult.PASSED
        return CheckResult.UNKNOWN


check = NetworkACLRestrictsSSH()
