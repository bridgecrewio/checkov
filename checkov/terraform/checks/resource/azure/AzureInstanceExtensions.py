from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class AzureInstanceExtensions(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure Virtual Machine Extensions are not Installed"
        id = "CKV_AZURE_50"
        supported_resources = ['azurerm_virtual_machine', 'azurerm_linux_virtual_machine']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.PASSED)

    def get_inspected_key(self):
        return 'allow_extension_operations'

    def get_expected_value(self):
        return False


check = AzureInstanceExtensions()
