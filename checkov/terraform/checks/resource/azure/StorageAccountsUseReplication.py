from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from typing import Any, List


class StorageAccountsUseReplication(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that Storage Accounts use replication"
        id = "CKV_AZURE_206"
        supported_resources = ("azurerm_storage_account",)
        categories = (CheckCategories.BACKUP_AND_RECOVERY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "account_replication_type"

    def get_expected_value(self) -> Any:
        return "GRS"

    def get_expected_values(self) -> List[Any]:
        return ["GRS", "RAGRS", "GZRS", "RAGZRS"]


check = StorageAccountsUseReplication()
