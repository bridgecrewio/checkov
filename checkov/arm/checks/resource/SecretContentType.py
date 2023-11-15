from __future__ import annotations

from typing import Any
from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckCategories
from checkov.arm.base_resource_value_check import BaseResourceValueCheck


class SecretContentType(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = 'Ensure that key vault secrets have "content_type" set'
        id = "CKV_AZURE_114"
        supported_resources = ("Microsoft.KeyVault/vaults/secrets",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "properties/contentType"

    def get_expected_value(self) -> Any:
        return ANY_VALUE


check = SecretContentType()
