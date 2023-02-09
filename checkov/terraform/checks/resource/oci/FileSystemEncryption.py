from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.consts import ANY_VALUE


class FileSystemEncryption(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure OCI File System is Encrypted with a customer Managed Key"
        id = "CKV_OCI_15"
        supported_resources = ['oci_file_storage_file_system']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'kms_key_id'

    def get_expected_value(self):
        return ANY_VALUE


check = FileSystemEncryption()
