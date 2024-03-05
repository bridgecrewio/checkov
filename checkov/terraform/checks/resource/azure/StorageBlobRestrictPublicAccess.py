from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class StorageBlobRestrictPublicAccess(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that Storage blobs restrict public access"
        id = "CKV_AZURE_190"
        supported_resources = ("azurerm_storage_account",)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_resources=supported_resources,
        )

    def get_inspected_key(self) -> str:
        return "allow_nested_items_to_be_public"

    def get_expected_values(self) -> list[Any]:
        return [False]


check = StorageBlobRestrictPublicAccess()
