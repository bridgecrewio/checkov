from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class AppServiceFTPSState(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure FTP deployments are disabled"
        id = "CKV_AZURE_78"
        supported_resources = ('azurerm_app_service', 'azurerm_linux_web_app', 'azurerm_windows_web_app')
        categories = (CheckCategories.APPLICATION_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "site_config/0/ftps_state"

    def get_expected_value(self):
        return "Disabled"

    def get_expected_values(self):
        return ["Disabled", "FtpsOnly"]


check = AppServiceFTPSState()
