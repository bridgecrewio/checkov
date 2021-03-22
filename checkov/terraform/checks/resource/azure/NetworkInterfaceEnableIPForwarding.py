from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class NetworkInterfaceEnableIPForwarding(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that Network Interfaces disable IP forwarding"
        id = "CKV_AZURE_118"
        supported_resources = ['azurerm_network_interface']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.PASSED)

    def get_inspected_key(self):
        return 'enable_ip_forwarding'

    def get_expected_value(self):
        return False


check = NetworkInterfaceEnableIPForwarding()
