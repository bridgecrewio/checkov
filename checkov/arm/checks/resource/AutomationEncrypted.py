from checkov.arm.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class AutomationEncrypted(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that Automation account variables are encrypted"
        id = "CKV_AZURE_73"
        supported_resources = ("Microsoft.Automation/automationAccounts/variables",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "properties/isEncrypted"

    def get_expected_value(self) -> bool:
        return True


check = AutomationEncrypted()
