from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class AppServiceDetailedErrorMessagesEnabled(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that App service enables detailed error messages"
        id = "CKV_AZURE_65"
        supported_resources = ['azurerm_app_service']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "logs/[0]/detailed_error_messages_enabled"


check = AppServiceDetailedErrorMessagesEnabled()
