from ipaddress import ip_network, ip_address
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class VnetLocalDNS(BaseResourceCheck):
    def __init__(self):
        """Avoid taking a dependency on external DNS servers
         for local communication such as those deployed on-premises.
        Where possible consider deploying Azure Private DNS Zones,
         a platform-as-a-service (PaaS) DNS service for VNETs"""
        name = "Ensure that VNET use local DNS addresses"
        id = "CKV_AZURE_183"
        supported_resources = ['azurerm_virtual_network']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'dns_servers' in conf:
            dns_servers = conf.get('dns_servers')[0]
            for ip in dns_servers:
                ranges = conf.get('address_space')[0]
                for myRange in ranges:
                    net = ip_network(myRange)
                    if ip_address(ip) in net:
                        return CheckResult.PASSED
            self.evaluated_keys = ['dns_servers']
            return CheckResult.FAILED
        return CheckResult.PASSED


check = VnetLocalDNS()
