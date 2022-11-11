from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories, CheckResult


class AppServiceDetailedErrorMessagesEnabled(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that App service enables detailed error messages"
        id = "CKV_AZURE_65"
        supported_resources = ('azurerm_app_service', 'azurerm_linux_web_app', 'azurerm_windows_web_app')
        categories = (CheckCategories.LOGGING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.FAILED)

    def get_inspected_key(self):
        if self.entity_type == 'azurerm_app_service':
            return "logs/[0]/detailed_error_messages_enabled"
        else:
            return "logs/[0]/detailed_error_messages"


check = AppServiceDetailedErrorMessagesEnabled()
