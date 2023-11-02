from typing import Any

from checkov.arm.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class AppServiceMinTLSVersion(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure web app is using the latest version of TLS encryption"
        id = "CKV_AZURE_15"
        supported_resources = ("Microsoft.Web/sites",)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        # https://docs.microsoft.com/en-us/azure/templates/microsoft.web/2019-08-01/sites
        return "properties/siteConfig/minTlsVersion"

    def get_expected_value(self) -> Any:
        return "1.2"


check = AppServiceMinTLSVersion()
