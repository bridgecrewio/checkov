from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck


class DataExplorerSKUHasSLA(BaseResourceNegativeValueCheck):
    def __init__(self) -> None:
        name = "Ensure that data explorer uses Sku with an SLA"
        id = "CKV_AZURE_180"
        supported_resources = ("azurerm_kusto_cluster",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_resources=supported_resources,
            missing_attribute_result=CheckResult.UNKNOWN,
        )

    def get_inspected_key(self) -> str:
        return "sku/[0]/name"

    def get_forbidden_values(self) -> list[Any]:
        return [
            "Dev(No SLA)_Standard_D11_v2",
            "Dev(No SLA)_Standard_E2a_v4",
        ]


check = DataExplorerSKUHasSLA()
