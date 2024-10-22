from __future__ import annotations
from checkov.arm.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class AppServiceDetailedErrorMessagesEnabled(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that App service enables detailed error messages"
        id = "CKV_AZURE_65"
        supported_resources = ['Microsoft.Web/sites/config']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "properties/detailedErrorLoggingEnabled"


check = AppServiceDetailedErrorMessagesEnabled()
