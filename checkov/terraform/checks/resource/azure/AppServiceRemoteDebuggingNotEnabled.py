from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class AppServiceRemoteDebuggingNotEnabled(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that remote debugging is not enabled for app services"
        id = "CKV_AZURE_72"
        supported_resources = ('azurerm_app_service',
                               'azurerm_linux_function_app',
                               'azurerm_linux_function_app_slot',
                               'azurerm_linux_web_app',
                               'azurerm_linux_web_app_slot',
                               'azurerm_windows_function_app',
                               'azurerm_windows_function_app_slot',
                               'azurerm_windows_web_app',
                               'azurerm_windows_web_app_slot'
                               )
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.PASSED)

    def get_inspected_key(self) -> str:
        return "site_config/[0]/remote_debugging_enabled"

    def get_expected_value(self) -> Any:
        return False


check = AppServiceRemoteDebuggingNotEnabled()
