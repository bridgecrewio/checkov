from checkov.common.models.enums import CheckCategories
from checkov.arm.base_resource_value_check import BaseResourceValueCheck


class AppServiceDotnetFrameworkVersion(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that 'Net Framework' version is the latest, if used as a part of the web app"
        id = "CKV_AZURE_80"
        supported_resources = ['Microsoft.Web/sites/config']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "properties/netFrameworkVersion"

    def get_expected_value(self) -> str:
        return "v8.0"


check = AppServiceDotnetFrameworkVersion()
