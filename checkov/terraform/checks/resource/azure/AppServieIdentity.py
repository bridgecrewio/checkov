from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.consts import ANY_VALUE


class AppServiceIdentity(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that Register with Azure Active Directory is enabled on App Service"
        id = "CKV_AZURE_16"
        supported_resources = ['azurerm_app_service']
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'identity'

    def get_expected_values(self):
        return ANY_VALUE


check = AppServiceIdentity()
