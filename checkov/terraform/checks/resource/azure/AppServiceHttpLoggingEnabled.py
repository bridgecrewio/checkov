from checkov.common.models.consts import ANY_VALUE
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class AppServiceHttpLoggingEnabled(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that App service enables HTTP logging"
        id = "CKV_AZURE_63"
        supported_resources = ['azurerm_app_service']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "logs/[0]/http_logs"

    def get_expected_value(self):
        return ANY_VALUE


check = AppServiceHttpLoggingEnabled()
