from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class NACLInboundCheck(BaseResourceCheck):
    def __init__(self, check_id, port):
        name = "Ensure no NACL allow inbound from 0.0.0.0:0 to port %d" % port
        id = check_id
        supported_resources = ['ncloud_network_acl_rule']

        categories = [CheckCategories.NETWORKING]
        guideline = "You should Ensure no NACL allow inbound from 0.0.0.0:0 to port %d" % port
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources, guideline=guideline)
        self.port = port

    def scan_resource_conf(self, conf):
        if 'inbound' in conf.keys():
            for inbound in conf['inbound']:
                if inbound['rule_action'] == ["ALLOW"]:
                    ip = inbound.get('ip_block', '0.0.0.0/0')[0]
                    if ip == '0.0.0.0/0' or ip == '::/0':
                        port = inbound.get('port_range', str(self.port))[0]
                        if port == str(self.port):
                            return CheckResult.FAILED
                        elif port.find('-'):
                            portRange = list(map(int, port.split("-")))
                            if portRange[0] <= self.port <= portRange[-1]:
                                return CheckResult.FAILED

        return CheckResult.PASSED
