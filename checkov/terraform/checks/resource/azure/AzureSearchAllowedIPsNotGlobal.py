from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck


class AzureSearchAllowedIPsNotGlobal(BaseResourceNegativeValueCheck):
    def __init__(self) -> None:
        # Setting the allowed ips to include global routes CIDR - 0.0.0.0/0 makes the resource public
        name = "Ensure Azure Cognitive Search service allowed IPS does not give public Access"
        id = "CKV_AZURE_210"
        supported_resources = ("azurerm_search_service",)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "allowed_ips"

    def get_forbidden_values(self) -> list[Any]:
        return ["0.0.0.0/0"]


check = AzureSearchAllowedIPsNotGlobal()
