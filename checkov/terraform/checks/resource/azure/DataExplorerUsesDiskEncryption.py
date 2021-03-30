from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class DataExplorerUsesDiskEncryption(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that Azure Data Explorer uses disk encryption"
        id = "CKV_AZURE_74"
        supported_resources = ['azurerm_kusto_cluster']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'enable_disk_encryption'


check = DataExplorerUsesDiskEncryption()
