from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class VMEncryptionAtHostEnabled(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that Virtual machine scale sets have encryption at host enabled"
        id = "CKV_AZURE_97"
        supported_resources = ['azurerm_linux_virtual_machine_scale_set', 'azurerm_windows_virtual_machine_scale_set']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return 'encryption_at_host_enabled'


check = VMEncryptionAtHostEnabled()
