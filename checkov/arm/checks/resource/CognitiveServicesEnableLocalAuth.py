from typing import Any

from checkov.common.models.enums import CheckCategories
from checkov.arm.base_resource_value_check import BaseResourceValueCheck


class CognitiveServicesEnableLocalAuth(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that Cognitive Services accounts enable local authentication"
        id = "CKV_AZURE_236"
        supported_resources = ('Microsoft.CognitiveServices/accounts', )
        categories = (CheckCategories.NETWORKING, )
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_resources=supported_resources,
        )

    def get_inspected_key(self) -> str:
        return 'properties/disableLocalAuth'

    def get_expected_value(self) -> Any:
        return True


check = CognitiveServicesEnableLocalAuth()
