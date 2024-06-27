from __future__ import annotations
from checkov.common.models.enums import CheckCategories
from checkov.arm.base_resource_value_check import BaseResourceValueCheck


class ACREnableImageQuarantine(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure container image quarantine, scan, and mark images verified"
        id = "CKV_AZURE_166"
        supported_resources = ("Microsoft.ContainerRegistry/registries",)
        categories = (CheckCategories.SUPPLY_CHAIN,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "properties/policies/quarantinePolicy/status"

    def get_expected_value(self) -> str:
        return "enabled"


check = ACREnableImageQuarantine()
