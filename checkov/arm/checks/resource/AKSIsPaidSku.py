from typing import Any

from checkov.common.models.enums import CheckCategories
from checkov.arm.base_resource_value_check import BaseResourceValueCheck


class AKSIsPaidSku(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that AKS use the Paid Sku for its SLA"
        id = "CKV_AZURE_170"
        supported_resources = ("Microsoft.ContainerService/managedClusters",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,)

    def get_inspected_key(self) -> str:
        return "sku/tier"

    def get_expected_value(self) -> Any:
        return "Standard"


check = AKSIsPaidSku()
