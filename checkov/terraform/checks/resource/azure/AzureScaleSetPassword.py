from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class AzureScaleSetPassword(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure Azure linux scale set does not use basic authentication(Use SSH Key Instead)"
        id = "CKV_AZURE_49"
        supported_resources = ['azurerm_linux_virtual_machine_scale_set']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "disable_password_authentication/[0]"


check = AzureScaleSetPassword()
