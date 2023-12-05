from checkov.common.models.enums import CheckCategories
from checkov.arm.base_resource_value_check import BaseResourceValueCheck


class WinVMEncryptionAtHost(BaseResourceValueCheck):
    def __init__(self) -> None:
        """
        If enabled, all the disks (including the temp disk) attached to this Virtual Machine will be encrypted

        If not enabled:
        https://learn.microsoft.com/en-gb/azure/virtual-machines/disks-enable-host-based-encryption-portal?tabs=azure-cli#prerequisites

        """
        name = "Ensure Windows VM enables encryption"
        id = "CKV_AZURE_151"
        supported_resources = ("Microsoft.Compute/virtualMachines",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "properties/securityProfile/encryptionAtHost"


check = WinVMEncryptionAtHost()
