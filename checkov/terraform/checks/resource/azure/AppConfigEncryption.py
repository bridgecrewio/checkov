from checkov.common.models.consts import ANY_VALUE

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from typing import Any


class AppConfigEncryption(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure App configuration encryption block is set."
        id = "CKV_AZURE_186"
        supported_resources = ("azurerm_app_configuration",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "encryption/[0]/key_vault_key_identifier"

    def get_expected_value(self) -> Any:
        return ANY_VALUE


check = AppConfigEncryption()
