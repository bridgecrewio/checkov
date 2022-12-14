from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class WinVMAutomaticUpdates(BaseResourceValueCheck):
    def __init__(self) -> None:
        """
        If enabled, updates are automatically applied
        """
        name = "Ensure Windows VM enables automatic updates"
        id = "CKV_AZURE_177"
        supported_resources = ("azurerm_windows_virtual_machine", "azurerm_windows_virtual_machine_scale_set")
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "enable_automatic_updates"


check = WinVMAutomaticUpdates()
