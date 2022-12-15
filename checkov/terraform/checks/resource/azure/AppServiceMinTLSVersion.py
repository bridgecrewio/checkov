from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class AppServiceMinTLSVersion(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure web app is using the latest version of TLS encryption"
        id = "CKV_AZURE_15"
        supported_resources = ('azurerm_app_service', 'azurerm_linux_web_app', 'azurerm_windows_web_app')
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.PASSED)

    def get_inspected_key(self):
        if self.entity_type == "azurerm_app_service":
            return "site_config/[0]/min_tls_version/[0]"
        else:
            return "site_config/[0]/minimum_tls_version/[0]"

    def get_expected_value(self):
        return '1.2'


check = AppServiceMinTLSVersion()
