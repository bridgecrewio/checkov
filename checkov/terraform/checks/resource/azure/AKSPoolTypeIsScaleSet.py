from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck


class AKSPoolTypeIsScaleSet(BaseResourceNegativeValueCheck):
    def __init__(self) -> None:
        name = "Ensure Azure Kubernetes Cluster (AKS) nodes use scale sets"
        id = "CKV_AZURE_169"
        supported_resources = ("azurerm_kubernetes_cluster",)
        categories = (CheckCategories.KUBERNETES,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "default_node_pool/[0]/type"

    def get_forbidden_values(self) -> list[Any]:
        return ["AvailabilitySet"]


check = AKSPoolTypeIsScaleSet()
