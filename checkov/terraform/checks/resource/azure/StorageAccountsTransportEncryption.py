from checkov.terraform.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_check import BaseResourceCheck


class StorageAccountsTransportEncryption(BaseResourceCheck):
    def __init__(self):
        name = "Ensure that 'Secure transfer required' is set to 'Enabled'"
        id = "CKV_AZURE_3"
        supported_resources = ['azurerm_storage_account']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for traffic encryption configuration at azurerm_storage_account:
            https://www.terraform.io/docs/providers/azurerm/r/storage_account.html
        :param conf: azure_instance configuration
        :return: <CheckResult>
        """
        if 'enable_https_traffic_only' in conf.keys():
            config = conf['enable_https_traffic_only'][0]
            if config:
                return CheckResult.PASSED
        return CheckResult.FAILED


check = StorageAccountsTransportEncryption()
