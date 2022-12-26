from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck


class SignalRSJUSLA(BaseResourceNegativeValueCheck):
    def __init__(self) -> None:
        name = "Ensure that SignalR uses a Paid Sku for its SLA"
        id = "CKV_AZURE_196"
        supported_resources = ("azurerm_signalr_service",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "sku/[0]/name"

    def get_forbidden_values(self) -> list[Any]:
        return ["Free_F1"]


check = SignalRSJUSLA()
