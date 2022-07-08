from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class FunctionAppEnableLogging(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure function app builtin logging is enabled"
        id = "CKV_AZURE_159"
        supported_resources = ['azurerm_function_app', 'azurerm_function_app_slot']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.PASSED)

    def get_inspected_key(self):
        return 'enable_builtin_logging'


check = FunctionAppEnableLogging()
