from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class AppServiceSlotHTTPSOnly(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure web app redirects all HTTP traffic to HTTPS in Azure App Service Slot"
        id = "CKV_AZURE_153"
        supported_resources = ["azurerm_app_service_slot", "azurerm_linux_web_app_slot", "azurerm_windows_web_app_slot"]
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "https_only/[0]"


check = AppServiceSlotHTTPSOnly()
