from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from typing import Any
from checkov.common.models.consts import ANY_VALUE


class LinuxVMUsesSSH(BaseResourceValueCheck):
    def __init__(self) -> None:
        """
        If enabled, Uses SSH
        """
        name = "Ensure linux VM enables SSH with keys for secure communication"
        id = "CKV_AZURE_178"
        supported_resources = ("azurerm_linux_virtual_machine", "azurerm_linux_virtual_machine_scale_set")
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "admin_ssh_key/[0]/public_key"

    def get_expected_value(self) -> Any:
        return ANY_VALUE


check = LinuxVMUsesSSH()
