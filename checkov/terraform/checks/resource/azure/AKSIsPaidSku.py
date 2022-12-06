from typing import Any

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class AKSIsPaidSku(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that AKS use the Paid Sku for its SLA"
        # AKS clusters should have Uptime
        # SLA enabled to ensure availability
        # of control plane components
        # for production workloads.
        id = "CKV_AZURE_170"
        supported_resources = ("azurerm_kubernetes_cluster",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "sku_tier"

    def get_expected_value(self) -> Any:
        return "Paid"


check = AKSIsPaidSku()
