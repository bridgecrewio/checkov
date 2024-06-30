from checkov.common.models.consts import ANY_VALUE
from typing import Any
from checkov.common.models.enums import CheckCategories
from checkov.arm.base_resource_value_check import BaseResourceValueCheck


class AzureBatchAccountUsesKeyVaultEncryption(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that Azure Batch account uses key vault to encrypt data"
        id = "CKV_AZURE_76"
        supported_resources = ("Microsoft.Batch/batchAccounts",)
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,)

    def get_inspected_key(self) -> str:
        return "properties/keyVaultReference"

    def get_expected_value(self) -> Any:
        return ANY_VALUE


check = AzureBatchAccountUsesKeyVaultEncryption()
