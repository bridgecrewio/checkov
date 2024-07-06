from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckCategories
from checkov.arm.base_resource_negative_value_check import BaseResourceNegativeValueCheck


class PubsubSKUSLA(BaseResourceNegativeValueCheck):
    def __init__(self) -> None:
        name = "Ensure Web PubSub uses a SKU with an SLA"
        id = "CKV_AZURE_175"
        supported_resources = ("Microsoft.SignalRService/webPubSub",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,)

    def get_inspected_key(self) -> str:
        return "sku/name"

    def get_forbidden_values(self) -> Any:
        return "Free_F1"


check = PubsubSKUSLA()
