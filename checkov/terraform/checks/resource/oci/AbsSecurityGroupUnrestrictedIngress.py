from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class AbsSecurityGroupUnrestrictedIngress(BaseResourceCheck):
    def __init__(self, check_id, port):
        name = f"Ensure no security groups rules allow ingress from 0.0.0.0:0 to port {port}"
        supported_resources = ['oci_core_network_security_group_security_rule']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=check_id, categories=categories, supported_resources=supported_resources)
        self.port = port

    def scan_resource_conf(self, conf):
        direction = conf.get('direction')
        source = conf.get('source')
        protocol = conf.get('protocol')
        tcp_options = conf.get('tcp_options')
        if direction and direction[0] != 'INGRESS':
            return CheckResult.PASSED
        if source and source[0] != "0.0.0.0/0":
            return CheckResult.PASSED
        elif (tcp_options is None and protocol[0] == 'all') \
                or tcp_options and self.scan_protocol_conf(tcp_options) is False:
            return CheckResult.FAILED
        return CheckResult.PASSED

    def scan_protocol_conf(self, protocol_name):
        """ scan tcp_options configuration"""
        max_port = protocol_name[0]['source_port_range'][0]['max'][0]
        min_port = protocol_name[0]['source_port_range'][0]['min'][0]
        if min_port <= self.port <= max_port:
            return False
        return True
