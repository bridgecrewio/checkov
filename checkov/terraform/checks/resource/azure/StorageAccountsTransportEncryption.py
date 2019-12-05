from checkov.terraform.models.enums import ScanResult, ScanCategories
from checkov.terraform.checks.resource.base_check import BaseResourceCheck


class StorageAccountsTransportEncryption(BaseResourceCheck):
    def __init__(self):
        name = "Ensure that 'Secure transfer required' is set to 'Enabled'"
        scan_id = "BC_AZURE_STORAGE_1"
        supported_resources = ['azurerm_storage_account']
        categories = [ScanCategories.ENCRYPTION]
        super().__init__(name=name, scan_id=scan_id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for traffic encryption configuration at azurerm_storage_account:
            https://www.terraform.io/docs/providers/azurerm/r/storage_account.html
        :param conf: azure_instance configuration
        :return: <ScanResult>
        """
        if 'enable_https_traffic_only' in conf.keys():
            config = conf['enable_https_traffic_only'][0]
            if config == True:
                return ScanResult.SUCCESS
        return ScanResult.FAILURE


scanner = StorageAccountsTransportEncryption()
