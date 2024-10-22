from typing import Any

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class DataFactoryNoPublicNetworkAccess(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that Azure Data factory public network access is disabled"
        id = "CKV_AZURE_104"
        supported_resources = ("azurerm_data_factory",)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "public_network_enabled"

    def get_expected_value(self) -> Any:
        return False


check = DataFactoryNoPublicNetworkAccess()
