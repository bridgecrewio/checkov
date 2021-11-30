from typing import Any

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class AzureInstanceExtensions(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure Virtual Machine Extensions are not Installed"
        id = "CKV_AZURE_50"
        supported_resources = ["azurerm_linux_virtual_machine", "azurerm_windows_virtual_machine"]
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "allow_extension_operations"

    def get_expected_value(self) -> Any:
        return False


check = AzureInstanceExtensions()
