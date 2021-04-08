from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class FunctionAppsAccessibleOverHttps(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that Function apps is only accessible over HTTPS"
        id = "CKV_AZURE_70"
        supported_resources = ['azurerm_function_app']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'https_only'


check = FunctionAppsAccessibleOverHttps()
