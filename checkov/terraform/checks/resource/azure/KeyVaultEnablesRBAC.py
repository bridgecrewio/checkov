from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories
from checkov.common.models.enums import CheckResult


class KeyVaultEnablesRBAC(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure RBAC for Azure Key Vault is enabled"
        id = "CKV_AZURE_242"
        supported_resources = ['azurerm_key_vault']
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.PASSED)

    def get_inspected_key(self):
        return "enable_rbac_authorization"


check = KeyVaultEnablesRBAC()
