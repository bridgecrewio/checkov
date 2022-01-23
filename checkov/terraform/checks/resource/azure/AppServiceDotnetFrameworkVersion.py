from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class AppServiceDotnetFrameworkVersion(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that 'Net Framework' version is the latest, if used as a part of the web app"
        id = "CKV_AZURE_80"
        supported_resources = ['azurerm_app_service']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "site_config/0/dotnet_framework_version"

    def get_expected_value(self):
        return "v6.0"


check = AppServiceDotnetFrameworkVersion()
