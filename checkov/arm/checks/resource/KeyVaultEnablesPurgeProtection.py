from typing import Any

from checkov.common.models.enums import CheckCategories
from checkov.arm.base_resource_value_check import BaseResourceValueCheck


class KeyVaultEnablesPurgeProtection(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that key vault enables purge protection"
        id = "CKV_AZURE_110"
        supported_resources = ['Microsoft.KeyVault/vaults']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> Any:
        return "properties/enablePurgeProtection"

    def get_expected_value(self) -> bool:
        return True


check = KeyVaultEnablesPurgeProtection()
