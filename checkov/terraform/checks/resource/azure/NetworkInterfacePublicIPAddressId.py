from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceCheck


class NetworkInterfacePublicIPAddressId(BaseResourceCheck):
    def __init__(self):
        name = "Ensure that Network Interfaces don't use public IPs"
        id = "CKV_AZURE_119"
        supported_resources = ['azurerm_network_interface']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        ip_configurations = conf.get('ip_configuration', [])
        for ip_configuration in ip_configurations:
            if 'public_ip_address_id' in ip_configuration:
                return CheckResult.FAILED
        return CheckResult.PASSED


check = NetworkInterfacePublicIPAddressId()
