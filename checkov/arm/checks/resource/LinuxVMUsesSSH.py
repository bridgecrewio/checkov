from checkov.common.models.enums import CheckCategories
from checkov.arm.base_resource_value_check import BaseResourceValueCheck
from typing import Any
from checkov.common.models.consts import ANY_VALUE


class LinuxVMUsesSSH(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure linux VM enables SSH with keys for secure communication"
        id = "CKV_AZURE_178"
        supported_resources = ("Microsoft.Compute/virtualMachines", "Microsoft.Compute/virtualMachineScaleSets")
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,)

    def get_inspected_key(self) -> str:
        if self.entity_type == "Microsoft.Compute/virtualMachineScaleSets":
            return "properties/virtualMachineProfile/osProfile/linuxConfiguration/ssh/publicKeys/[0]/path"
        return "properties/osProfile/linuxConfiguration/ssh/publicKeys/[0]/path"

    def get_expected_value(self) -> Any:
        return ANY_VALUE


check = LinuxVMUsesSSH()
