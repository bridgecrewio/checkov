from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck


class AppServiceDisallowCORS(BaseResourceNegativeValueCheck):
    def __init__(self):
        name = "Ensure that CORS disallows every resource to access app services"
        id = "CKV_AZURE_57"
        supported_resources = ['azurerm_app_service']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources, missing_attribute_result=CheckResult.PASSED)

    def get_inspected_key(self):
        return 'site_config/[0]/cors/[0]/allowed_origins'

    def get_forbidden_values(self):
        return [['*']]


check = AppServiceDisallowCORS()
