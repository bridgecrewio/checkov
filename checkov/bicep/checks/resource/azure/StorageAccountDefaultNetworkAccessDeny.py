from __future__ import annotations

from typing import Any

from checkov.bicep.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class StorageAccountDefaultNetworkAccessDeny(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure default network access rule for Storage Accounts is set to deny"
        id = "CKV_AZURE_35"
        supported_resources = ("Microsoft.Storage/storageAccounts",)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "properties/networkAcls/defaultAction"

    def get_expected_value(self) -> Any:
        return "Deny"


check = StorageAccountDefaultNetworkAccessDeny()
