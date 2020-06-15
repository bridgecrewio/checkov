from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceCheck


class StorageAccountAzureServicesAccessEnabled(BaseResourceCheck):
    def __init__(self):
        name = "Ensure 'Trusted Microsoft Services' is enabled for Storage Account access"
        id = "CKV_AZURE_36"
        supported_resources = ['azurerm_storage_account', 'azurerm_storage_account_network_rules']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        network_conf = [conf]
        if 'network_rules' in conf:
            network_conf = conf['network_rules']
        if 'bypass' in network_conf[0]:
            if 'AzureServices' not in network_conf[0]['bypass'][0]:
                return CheckResult.FAILED
        return CheckResult.PASSED


check = StorageAccountAzureServicesAccessEnabled()
