from typing import Any

from checkov.common.models.enums import CheckCategories
from checkov.arm.base_resource_value_check import BaseResourceValueCheck


class CognitiveServicesDisablesPublicNetwork(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that Cognitive Services accounts disable public network access"
        id = "CKV_AZURE_134"
        supported_resources = ("Microsoft.CognitiveServices/accounts",)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "properties/publicNetworkAccess"

    def get_expected_value(self) -> Any:
        return "Disabled"


check = CognitiveServicesDisablesPublicNetwork()
