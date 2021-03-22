from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class AppServiceEnableFailedRequest(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that App service enables failed request tracing"
        id = "CKV_AZURE_66"
        supported_resources = ['azurerm_app_service']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'logs/[0]/failed_request_tracing_enabled'


check = AppServiceEnableFailedRequest()
