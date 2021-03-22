from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class RemoteDebuggingNotEnabled(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that remote debugging is not enabled for app services"
        id = "CKV_AZURE_72"
        supported_resources = ['azurerm_app_service']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.PASSED)

    def get_inspected_key(self):
        return "remote_debugging_enabled"

    def get_expected_value(self):
        return False


check = RemoteDebuggingNotEnabled()
