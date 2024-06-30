from checkov.arm.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class FunctionAppsEnableAuthentication(BaseResourceValueCheck):

    def __init__(self) -> None:
        name = "Ensure that function apps enables Authentication"
        id = "CKV_AZURE_56"
        supported_resources = ("Microsoft.Web/sites/config",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name,
                         id=id,
                         categories=categories,
                         supported_resources=supported_resources,

                         )

    def get_inspected_key(self) -> str:
        return 'properties/platform/enabled'


check = FunctionAppsEnableAuthentication()
