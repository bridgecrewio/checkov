from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck


class AKSUpgradeChannel(BaseResourceNegativeValueCheck):
    def __init__(self) -> None:
        name = "Ensure AKS cluster upgrade channel is chosen"
        id = "CKV_AZURE_171"
        supported_resources = ("azurerm_kubernetes_cluster",)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_resources=supported_resources,
            missing_attribute_result=CheckResult.FAILED,
        )

    def get_inspected_key(self) -> str:
        return "automatic_channel_upgrade"

    def get_forbidden_values(self) -> list[Any]:
        return ["none"]


check = AKSUpgradeChannel()
