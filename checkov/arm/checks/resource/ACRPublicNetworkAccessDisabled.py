
from __future__ import annotations
from checkov.common.models.enums import CheckCategories
from checkov.arm.base_resource_value_check import BaseResourceValueCheck


class ACRPublicNetworkAccessDisabled(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure ACR set to disable public networking"
        id = "CKV_AZURE_139"
        supported_resources = ("Microsoft.ContainerRegistry/registries",)
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "properties/publicNetworkAccess"

    def get_expected_value(self) -> str:
        return "Disabled"


check = ACRPublicNetworkAccessDisabled()
