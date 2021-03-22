from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class AzureManagedDiskEncryptionSet(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that managed disks use a specific set of disk encryption sets for the " \
               "customer-managed key encryption"
        id = "CKV_AZURE_93"
        supported_resources = ['azurerm_managed_disk']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'disk_encryption_set_id'

    def get_expected_value(self):
        return ANY_VALUE


check = AzureManagedDiskEncryptionSet()
