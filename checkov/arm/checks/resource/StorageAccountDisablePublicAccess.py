from __future__ import annotations

from typing import Any

from checkov.arm.base_resource_negative_value_check import BaseResourceNegativeValueCheck
from checkov.common.models.enums import CheckCategories


class StorageAccountDisablePublicAccess(BaseResourceNegativeValueCheck):
    def __init__(self) -> None:
        name = "Ensure that Storage accounts disallow public access"
        id = "CKV_AZURE_59"
        supported_resources = ("Microsoft.Storage/storageAccounts",)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "properties/publicNetworkAccess"

    def get_forbidden_values(self) -> list[Any]:
        return ["Enabled"]


check = StorageAccountDisablePublicAccess()
