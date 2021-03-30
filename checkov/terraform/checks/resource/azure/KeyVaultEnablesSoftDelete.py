from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories
from checkov.common.models.enums import CheckResult


class KeyVaultEnablesSoftDelete(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that key vault enables soft delete"
        id = "CKV_AZURE_111"
        supported_resources = ['azurerm_key_vault']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.PASSED)

    def get_inspected_key(self):
        return "soft_delete_enabled"


check = KeyVaultEnablesSoftDelete()
