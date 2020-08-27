from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class StorageAccountMinimumTlsVersion(BaseResourceCheck):
    """
        Looks for min_tls_version configuration at azurerm_storage_account to be set to TLS1_2
        https://www.terraform.io/docs/providers/azurerm/r/storage_account.html#min_tls_version
        :param conf: azurerm_storage_account configuration
        :return: <CheckResult>
    """
    def __init__(self):
        name = "Ensure Storage Account is using the latest version of TLS encryption"
        id = "CKV_AZURE_44"
        supported_resources = ['azurerm_storage_account']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'min_tls_version' not in conf or \
                conf['min_tls_version'][0] == 'TLS1_0' or conf['min_tls_version'][0] == 'TLS1_1':
            return CheckResult.FAILED
        return CheckResult.PASSED


check = StorageAccountMinimumTlsVersion()
