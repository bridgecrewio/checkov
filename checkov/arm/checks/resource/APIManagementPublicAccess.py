from typing import Any

from checkov.common.models.enums import CheckCategories
from checkov.arm.base_resource_value_check import BaseResourceValueCheck


class APIManagementPublicAccess(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure API management public access is disabled"
        id = "CKV_AZURE_174"
        supported_resources = ("Microsoft.ApiManagement/service",)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "properties/publicNetworkAccess"

    def get_expected_value(self) -> Any:
        return "Disabled"


check = APIManagementPublicAccess()
