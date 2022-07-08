from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class AppServiceSlotDebugDisabled(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure debugging is disabled for the App service slot"
        id = "CKV_AZURE_155"
        supported_resources = ['azurerm_app_service_slot']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.PASSED)

    def get_inspected_key(self):
        return "site_config/[0]/remote_debugging_enabled/[0]"

    def get_expected_value(self):
        return False


check = AppServiceSlotDebugDisabled()
