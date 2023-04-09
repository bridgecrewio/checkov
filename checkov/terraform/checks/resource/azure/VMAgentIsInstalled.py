from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class VMAgentIsInstalled(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure VM agent is installed"
        id = "CKV_AZURE_179"
        supported_resources = (
            "azurerm_windows_virtual_machine",
            "azurerm_windows_virtual_machine_scale_set",
            "azurerm_linux_virtual_machine_scale_set",
            "azurerm_linux_virtual_machine",
        )
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_resources=supported_resources, missing_block_result=CheckResult.PASSED
        )

    def get_inspected_key(self) -> str:
        return "provision_vm_agent"


check = VMAgentIsInstalled()
