from typing import Any

from checkov.arm.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class AppServiceHttps20Enabled(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that 'HTTP Version' is the latest if used to run the web app"
        id = "CKV_AZURE_18"
        supported_resources = ("Microsoft.Web/sites",)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        # https://docs.microsoft.com/en-us/azure/templates/microsoft.web/2019-08-01/sites
        return "properties/siteConfig/http20Enabled"

    def get_expected_value(self) -> Any:
        return "true"


check = AppServiceHttps20Enabled()
