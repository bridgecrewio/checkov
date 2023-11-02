from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckCategories
from checkov.arm.base_resource_value_check import BaseResourceValueCheck


class KeyBackedByHSM(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that key vault key is backed by HSM"
        id = "CKV_AZURE_112"
        supported_resources = ("Microsoft.KeyVault/vaults/keys",)
        categories = (CheckCategories.BACKUP_AND_RECOVERY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "properties/kty"

    def get_expected_value(self) -> Any:
        return "RSA-HSM"

    def get_expected_values(self) -> list[Any]:
        return [self.get_expected_value(), "EC-HSM"]


check = KeyBackedByHSM()
