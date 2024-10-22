from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class WinVMEncryptionAtHost(BaseResourceValueCheck):
    def __init__(self):
        """
        If enabled, all the disks (including the temp disk) attached to this Virtual Machine will be encrypted

        if not enabled:
        https://learn.microsoft.com/en-gb/azure/virtual-machines/disks-enable-host-based-encryption-portal?tabs=azure-cli#prerequisites
        """
        name = "Ensure Windows VM enables encryption"
        id = "CKV_AZURE_151"
        supported_resources = ['azurerm_windows_virtual_machine']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "encryption_at_host_enabled"


check = WinVMEncryptionAtHost()
