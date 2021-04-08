from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class KeyVaultEnablesPurgeProtection(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that key vault enables purge protection"
        id = "CKV_AZURE_110"
        supported_resources = ['azurerm_key_vault']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "purge_protection_enabled"


check = KeyVaultEnablesPurgeProtection()
