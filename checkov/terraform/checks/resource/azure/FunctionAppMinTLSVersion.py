from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class FunctionAppMinTLSVersion(BaseResourceValueCheck):
    def __init__(self):
        """
        The minimum supported TLS version for the function app.
        Defaults to 1.2 for new function apps.
        field name is:
         - min_tls_version in azurerm_function_app, azurerm_function_app_slot.
         - minimum_tls_version in newer resources (with linux/windows).
        """
        name = "Ensure Function app is using the latest version of TLS encryption"
        id = "CKV_AZURE_145"
        supported_resources = ['azurerm_function_app', 'azurerm_linux_function_app', 'azurerm_windows_function_app',
                               'azurerm_function_app_slot', 'azurerm_linux_function_app_slot',
                               'azurerm_windows_function_app_slot']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.PASSED)

    def get_inspected_key(self):
        if self.entity_type in ("azurerm_function_app", "azurerm_function_app_slot"):
            return "site_config/[0]/min_tls_version"
        else:
            return "site_config/[0]/minimum_tls_version"

    def get_expected_value(self):
        return 1.2

    def get_expected_values(self):
        return ["1.2", 1.2]


check = FunctionAppMinTLSVersion()
