from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class AzureBatchAccountUsesKeyVaultEncryption(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that Azure Batch account uses key vault to encrypt data"
        id = "CKV_AZURE_76"
        supported_resources = ['azurerm_batch_account']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'key_vault_reference/[0]/id'

    def get_expected_value(self):
        return ANY_VALUE


check = AzureBatchAccountUsesKeyVaultEncryption()
