from __future__ import annotations
from typing import Any, List
from checkov.common.models.enums import CheckCategories
from checkov.arm.base_resource_negative_value_check import BaseResourceNegativeValueCheck


class ACRAdminAccountDisabled(BaseResourceNegativeValueCheck):
    def __init__(self) -> None:
        name = "Ensure ACR admin account is disabled"
        id = "CKV_AZURE_137"
        supported_resources = ("Microsoft.ContainerRegistry/registries",)
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "properties/adminUserEnabled"

    def get_forbidden_values(self) -> List[Any]:
        return [True]


check = ACRAdminAccountDisabled()
