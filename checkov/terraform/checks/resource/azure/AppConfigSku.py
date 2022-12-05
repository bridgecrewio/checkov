
from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from typing import Any


class AppConfigSku(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure App configuration Sku is standard"
        id = "CKV_AZURE_188"
        supported_resources = ("azurerm_app_configuration",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "sku"

    def get_expected_value(self) -> Any:
        return "standard"


check = AppConfigSku()
