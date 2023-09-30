from typing import Any

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class FunctionAppPublicAccessDisabled(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that Azure Function App public network access is disabled"
        id = "CKV_AZURE_221"
        supported_resources = (
            "azurerm_linux_function_app",
            "azurerm_linux_function_app_slot",
            "azurerm_windows_function_app",
            "azurerm_windows_function_app_slot",
        )
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "public_network_access_enabled"

    def get_expected_value(self) -> Any:
        return False


check = FunctionAppPublicAccessDisabled()
