from typing import Any
from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckCategories
from checkov.arm.base_resource_value_check import BaseResourceValueCheck


class CognitiveServicesConfigureIdentity(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that all Azure Cognitive Services accounts are configured with a managed identity"
        id = "CKV_AZURE_238"
        supported_resources = ('Microsoft.CognitiveServices/accounts',)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "identity/type"

    def get_expected_value(self) -> Any:
        return ANY_VALUE


check = CognitiveServicesConfigureIdentity()
