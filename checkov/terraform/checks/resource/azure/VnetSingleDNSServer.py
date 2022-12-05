from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class VnetSingleDNSServer(BaseResourceCheck):
    def __init__(self):
        """Using a single DNS server may indicate a single point of failure
        where the DNS IP address is not load balanced."""
        name = "Ensure that VNET have a least 2 connected DNS Endpoints"
        id = "CKV_AZURE_182"
        supported_resources = ['azurerm_virtual_network', 'azurerm_virtual_network_dns_servers']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'dns_servers' in conf:
            dns_servers = conf.get('dns_servers')[0]
            if len(dns_servers) == 1:
                self.evaluated_keys = ['dns_servers']
                return CheckResult.FAILED
        return CheckResult.PASSED


check = VnetSingleDNSServer()
