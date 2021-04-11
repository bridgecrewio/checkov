from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.consts import ANY_VALUE


class SecurityCenterContactEmails(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that 'Security contact emails' is set"
        id = "CKV_AZURE_131"
        supported_resources = ['azurerm_security_center_contact']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "email"

    def get_expected_value(self):
        return ANY_VALUE


check = SecurityCenterContactEmails()
