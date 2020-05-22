from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class StorageAccountsTransportEncryption(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that 'Secure transfer required' is set to 'Enabled'"
        id = "CKV_AZURE_3"
        supported_resources = ['azurerm_storage_account']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'enable_https_traffic_only'


check = StorageAccountsTransportEncryption()
