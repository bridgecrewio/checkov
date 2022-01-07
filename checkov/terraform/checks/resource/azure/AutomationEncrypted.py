from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class AutomationEncrypted(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that Automation account variables are encrypted"
        id = "CKV_AZURE_73"
        supported_resources = (
            "azurerm_automation_variable_bool",
            "azurerm_automation_variable_string",
            "azurerm_automation_variable_int",
            "azurerm_automation_variable_datetime",
        )
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "encrypted"


check = AutomationEncrypted()
