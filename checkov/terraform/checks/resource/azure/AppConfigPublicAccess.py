from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck
from typing import List, Any


class AppConfigPublicAccess(BaseResourceNegativeValueCheck):
    def __init__(self) -> None:
        name = "Ensure 'Public Access' is not Enabled for App configuration"
        id = "CKV_AZURE_185"
        supported_resources = ("azurerm_app_configuration",)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "public_network_access"

    def get_forbidden_values(self) -> List[Any]:
        return ['Enabled']


check = AppConfigPublicAccess()
