from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class SecurityCenterStandardPricing(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that standard pricing tier is selected"
        id = "CKV_AZURE_19"
        supported_resources = ['azurerm_security_center_subscription_pricing']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'tier'

    def get_expected_value(self):
        return 'Standard'


check = SecurityCenterStandardPricing()
