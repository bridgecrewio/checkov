from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class AppServiceUsedAzureFiles(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that app services use Azure Files"
        id = "CKV_AZURE_88"
        supported_resources = ('azurerm_app_service', 'azurerm_linux_web_app', 'azurerm_windows_web_app')
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "storage_account/[0]/type"

    def get_expected_value(self):
        return 'AzureFiles'


check = AppServiceUsedAzureFiles()
