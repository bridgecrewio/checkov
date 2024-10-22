from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class AppServiceEnableFailedRequest(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that App service enables failed request tracing"
        id = "CKV_AZURE_66"
        supported_resources = ('azurerm_linux_web_app', 'azurerm_windows_web_app', 'azurerm_app_service')
        categories = (CheckCategories.LOGGING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        if self.entity_type == "azurerm_app_service":
            return 'logs/[0]/failed_request_tracing_enabled'
        else:
            return 'logs/[0]/failed_request_tracing'


check = AppServiceEnableFailedRequest()
