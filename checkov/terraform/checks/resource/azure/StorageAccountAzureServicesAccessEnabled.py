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
        if 'default_action' in network_conf[0]:
            # A required field in network rules, hence if dont exist there are no network rules and Azure services
            # have access --> Pass
            if network_conf[0]['default_action'][0] == 'Allow':
                return CheckResult.PASSED
            elif network_conf[0].get('bypass'):
                if 'AzureServices' in network_conf[0]['bypass'][0]:
                    return CheckResult.PASSED
                return CheckResult.FAILED
        return CheckResult.PASSED


check = StorageAccountAzureServicesAccessEnabled()
