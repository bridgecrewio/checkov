from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck


class APIManagementPublicAccess(BaseResourceNegativeValueCheck):
    def __init__(self) -> None:
        name = "Ensure API management public access is disabled"
        id = "CKV_AZURE_174"
        supported_resources = ("azurerm_api_management",)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_resources=supported_resources,
            missing_attribute_result=CheckResult.FAILED,
        )

    def get_inspected_key(self) -> str:
        return "public_network_access_enabled"

    def get_forbidden_values(self) -> list[Any]:
        return [True]


check = APIManagementPublicAccess()
