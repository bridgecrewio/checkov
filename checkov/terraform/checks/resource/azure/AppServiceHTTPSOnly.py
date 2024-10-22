from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class AppServiceHTTPSOnly(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure web app redirects all HTTP traffic to HTTPS in Azure App Service"
        id = "CKV_AZURE_14"
        supported_resources = ('azurerm_app_service', 'azurerm_linux_web_app', 'azurerm_windows_web_app')
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'https_only/[0]'


check = AppServiceHTTPSOnly()
