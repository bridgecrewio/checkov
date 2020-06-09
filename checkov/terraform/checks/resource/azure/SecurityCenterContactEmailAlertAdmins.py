from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class SecurityCenterEmailAlertAdmins(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that 'Send email notification for high severity alerts' is set to 'On'"
        id = "CKV_AZURE_22"
        supported_resources = ['azurerm_security_center_contact"']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'alerts_to_admins'


check = SecurityCenterEmailAlertAdmins()
