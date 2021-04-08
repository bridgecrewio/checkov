from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck


class FunctionAppDisallowCORS(BaseResourceNegativeValueCheck):
    def __init__(self):
        name = "Ensure function apps are not accessible from all regions"
        id = "CKV_AZURE_62"
        supported_resources = ['azurerm_function_app']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources, missing_attribute_result=CheckResult.PASSED)

    def get_inspected_key(self):
        return 'site_config/[0]/cors/[0]/allowed_origins'

    def get_forbidden_values(self):
        return [['*']]


check = FunctionAppDisallowCORS()
