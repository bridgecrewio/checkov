from typing import Any
from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckCategories
from checkov.arm.base_resource_value_check import BaseResourceValueCheck


class AppServiceIdentityProviderEnabled(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that Managed identity provider is enabled for web apps"
        id = "CKV_AZURE_71"
        supported_resources = ('Microsoft.Web/sites',)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "identity/type"

    def get_expected_value(self) -> Any:
        return ANY_VALUE


check = AppServiceIdentityProviderEnabled()
