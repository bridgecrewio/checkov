from checkov.common.models.consts import ANY_VALUE
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class GoogleComputeDiskEncryption(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure VM disks for critical VMs are encrypted with Customer Supplied Encryption Keys (CSEK)"
        id = "CKV_GCP_37"
        supported_resources = ['google_compute_disk']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'disk_encryption_key'

    def get_expected_value(self):
        return ANY_VALUE


check = GoogleComputeDiskEncryption()
