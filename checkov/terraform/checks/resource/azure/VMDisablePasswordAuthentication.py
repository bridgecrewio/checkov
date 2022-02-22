from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck


class VMDisablePasswordAuthentication(BaseResourceNegativeValueCheck):
    def __init__(self):
        name = "Ensure that Virtual machine does not enable password authentication"
        id = "CKV_AZURE_149"
        supported_resources = ['azurerm_linux_virtual_machine_scale_set', 'azurerm_linux_virtual_machine']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_forbidden_values(self) -> str:
        return [False]

    def get_inspected_key(self) -> str:
        return "disable_password_authentication"


check = VMDisablePasswordAuthentication()
